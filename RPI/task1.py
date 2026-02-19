import os
import json
import logging
from threading import Thread, Lock, Event
from time import time, sleep
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

from communications.android import Android
from communications.pc import PC
from communications.stm import STM

from streaming.stream_server import StreamServer

class Task1:
    """
    Class for managing Task 1 process.
    """

    def __init__(self):
        """
        Constructor for Task1.
        Initializes communication with Android tablet, PC, and STM32 microcontroller.
        """
        self.process_pc_stream = None
        self.pc_thread = None
        self.android_thread = None
        self.stm_thread = None
        
        self.android = Android()
        self.pc = PC()
        self.stm = STM()
        
        self.obstacles = []
        self.started = False
        
        self.segments = []
        self.segments_index = 0
        self.obstacle_order = []
        
        self.current_segment_commands = []  # Commands in the current segment
        self.command_index = 0  # Index within current segment
        
        self.directions = []
        self.direction_index = 0
        
        self._idx_lock = Lock()
        self.image_done = Event()
        
        self.timeout = 2  # seconds
        
    def stream_start(self):
        StreamServer().connect()
            
    def android_receive(self) -> None:
        while True:
            try:
                android_msg = self.android.receive()
                if not android_msg:
                    continue

                if android_msg == "BEGIN" and not self.started:
                    logging.info("Received BEGIN from Android, ending obstacle input.")
                    self.started = True
                    with self._idx_lock:
                        self.segments_index = 0
                        self.current_segment_commands = self.segments[self.segments_index]
                        self.segments_index += 1
                        self.command_index = 0
                    
                    # Send first command of first segment
                    if self.current_segment_commands:
                        cmd = self.current_segment_commands[self.command_index] + "\n"
                        self.command_index += 1
                        self.stm.send(cmd)
                        logging.info(f"Sent command {self.command_index}/{len(self.current_segment_commands)} to STM: {cmd.strip()}")
                else:
                    msg_parts = android_msg.split(',')
                    if msg_parts[0] == "OBSTACLE":
                        obstacle = {
                            "id": int(msg_parts[1]),
                            "x": int(msg_parts[2]) / 10,
                            "y": int(msg_parts[3]) / 10,
                            "d": {"NORTH": 0, "EAST": 2, "SOUTH": 4, "WEST": 6, "SKIP": 8}.get(msg_parts[4].strip())
                        }
                        self.obstacles.append(obstacle)
                        logging.info(f"Added obstacle: {obstacle}")
                    elif msg_parts[0] == "CLEAR":
                        self.obstacles = []
                        self.obstacle_order = []
                        logging.info("Cleared obstacles list.")
                    elif msg_parts[0] == "PATH":
                        self.pc.send("OBSTACLES," + json.dumps(self.obstacles))
            except OSError as e:
                print(f"Error: {e}")
                continue
            
    def pc_receive(self) -> None:
        while True:
            try:
                pc_msg = self.pc.receive()
                if pc_msg.startswith("PATH"):
                    path = json.loads(pc_msg.split("PATH,")[1])
                    logging.info(f"Received path segments: {path}")
                    self.segments = path['segments']
                    self.obstacle_order = path['obstacle_ids']
                    self.directions = path['dirs']
                elif pc_msg.startswith("OBJECT"):
                    self.image_done.set()
                    msg_split = pc_msg.replace("\n", "").split(",")[1:]

                    obstacle_id, conf_str, object_id = msg_split
                    confidence_level = None

                    try:
                        confidence_level = float(conf_str)
                    except ValueError:
                        confidence_level = None

                    logging.info(f"OBJECT ID: {object_id}")

                    if confidence_level is not None:
                        self.android.send(f"TARGET,{obstacle_id},{object_id}")

            except OSError as e:
                print(f"Error: {e}")
                continue
            
    def stm_receive(self) -> None:
        while True:
            try:
                stm_msg = self.stm.receive()
                if not stm_msg:
                    continue
                logging.info(f"Received from STM: {stm_msg}")
                if "RESEND" in stm_msg:
                    with self._idx_lock:
                        last_idx = max(self.segments_index - 1, 0)
                        cmd = ",".join(self.segments[last_idx]) + "\n"
                    self.stm.send(cmd)
                    logging.info(f"STM Error. Resending path segment{self.segments_index - 1}/{len(self.segments)}: {cmd}")
                    
                    self.image_done.wait(0.1)
                elif "OK" in stm_msg or "ACK" in stm_msg:
                    with self._idx_lock:
                        # Check if more commands in current segment
                        more_in_segment = self.command_index < len(self.current_segment_commands)
                        
                        if more_in_segment:
                            # Send next command in current segment
                            cmd = self.current_segment_commands[self.command_index] + "\n"
                            self.command_index += 1
                            self.stm.send(cmd)
                            logging.info(f"Sent command {self.command_index}/{len(self.current_segment_commands)} to STM: {cmd.strip()}")
                        else:
                            # Current segment finished, check for image detection
                            just_finished_idx = self.segments_index - 1
                            
                            if just_finished_idx >= 0 and just_finished_idx < len(self.obstacle_order):
                                self.image_done.clear()
                                message_content = f"DETECT,{self.obstacle_order[just_finished_idx]}"
                                self.pc.send(message_content)
                                self.image_done.wait(timeout=self.timeout)
                            
                            # Move to next segment
                            more_segments = self.segments_index < len(self.segments)
                            if more_segments:
                                self.current_segment_commands = self.segments[self.segments_index]
                                self.segments_index += 1
                                self.command_index = 0
                                
                                # Send first command of next segment
                                if self.current_segment_commands:
                                    cmd = self.current_segment_commands[self.command_index] + "\n"
                                    self.command_index += 1
                                    self.stm.send(cmd)
                                    logging.info(f"Sent command {self.command_index}/{len(self.current_segment_commands)} to STM: {cmd.strip()}")
                            else:
                                # All segments complete
                                self.pc.send(f'STITCH,{len(self.segments) - 1}')  # -1 for FIN segment
                                logging.info("All commands sent, requesting stitch.")
                elif "done" in stm_msg:
                    if self.direction_index < len(self.directions):
                        # x = self.directions[self.direction_index]['x']
                        # y = self.directions[self.direction_index]['y']
                        # direction = self.directions[self.direction_index]['d']
                        # # self.android.send(f"ROBOT,{y},{x},{direction}")
                        # self.direction_index += 1
                        continue
            except OSError as e:
                print(f"Error: {e}")
                continue
    
    def reconnect(self):
        # while not self.android.connected:
        #     self.android.accept_client()
        pass
        
    def start(self):
        """
        Run Task 1: communicate with Android, PC, and STM32.
        """
        logging.info("Starting Task 1.")
        self.android.start()
        self.pc.connect()
        self.stm.connect()
        
        self.process_pc_stream = Thread(target=self.stream_start)
        self.process_pc_stream.start()
        sleep(5)
        
        self.stm_thread = Thread(target=self.stm_receive)
        self.pc_thread = Thread(target=self.pc_receive)
        self.android_thread = Thread(target=self.android_receive)
        self.android_reconnect = Thread(target=self.reconnect)
        self.stm_thread.start()
        self.pc_thread.start()
        self.android_thread.start()
        
        self.stm_thread.join()
        self.pc_thread.join()
        self.android_thread.join()
        
        self.android_reconnect.start()
        self.android_reconnect.join()
        
        logging.info("Task 1 completed.")
        
if __name__ == "__main__":
    task1 = Task1()
    task1.start()
    

import math
import logging
from threading import Thread, Lock
from time import time, sleep, time_ns
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

from communications.android import Android
from communications.pc import PC
from communications.stm import STM

from streaming.stream_server import StreamServer

class Task2:
    """
    Class for managing Task 2 process.
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
        
        self.lock = Lock()
        self.obstacle_lock = Lock()
        self.last_image = None
        self.prev_image = None
        
        self.obstacle_order = []
        self.num_obstacle = 1
        self.timeout = 2  # seconds
        
        self.on_arrow_callback = None
        self.obstacle1_direction = None
        self.obstacle2_direction = None
        self.ultrasound_travelled_dist1 = None
        self.ultrasound_travelled_dist2 = None
        self.ultrasound_stop_dist1 = None
        self.ultrasound_stop_dist2 = None
        self.chassis_length = 28
        self.chassis_width = 19
        self.obstacle_length = 10
        self.slide_dist = 50
        self.turn_bias = 15
        self.extra_dist = 15
        self.center_offset_diag = 10
        self.center_offset_ninty = 7
        self.ninty_return_bias = 40
        self.turn_x = 30
        self.turn_y = 15
        self.ninty_threshold_length = 110.0
        self.ninty_threshold_width = 45.0
        
        self.LEFT_ARROW_ID = "39"
        self.RIGHT_ARROW_ID = "38"
        self.directions = {"39": "L", "38": "R"}
        self.wall_hug_length = None
        
        self.start_time = None
        self.end_time = None
        
    def stream_start(self):
        StreamServer().connect()
            
    def android_receive(self) -> None:
        while True:
            try:
                android_msg = self.android.receive()

                if android_msg == "BEGIN":
                    logging.info("Received BEGIN from Android")
                    self.start_time = time_ns()
                    self.ultrasound_forward(28)
                
            except OSError as e:
                print(f"Error: {e}")
                continue
            
    def pc_receive(self) -> None:
        while True:
            try:
                pc_msg = self.pc.receive()
                if not pc_msg:
                    continue
                if "NONE" in pc_msg:
                    self.set_last_image("NONE")
                else:
                    msg_split = pc_msg.replace("\n", "").split(",")
                    try:
                        conf_str, object_id = msg_split
                    except:
                        continue
                    confidence_level = None

                    try:
                        confidence_level = float(conf_str)
                    except ValueError:
                        confidence_level = None

                    if confidence_level:
                        if self.prev_image == None:
                            self.prev_image = object_id
                            self.set_last_image(object_id)
                        elif self.prev_image == object_id:
                            self.set_last_image(object_id)
                            pass
                        else:
                            self.prev_image = object_id
                            self.set_last_image(object_id)
                    else:
                        self.set_last_image("NONE")

            except OSError as e:
                print(f"Error: {e}")
                continue
            
    def stm_receive(self) -> None:
        while True:
            try:
                stm_msg = self.stm.wait_receive()
                logging.info(f"Received from STM: {stm_msg}")
                if "OK" in stm_msg:
                    if self.num_obstacle == 1:
                        direction = self.get_last_image()
                        logging.info(f"DIR: {direction}")
                        if direction in self.directions:
                            self.obstacle1_callback(direction)
                        else:
                            self.on_arrow_callback = self.obstacle1_callback
                        self.pc.send("SEEN")

                    elif self.num_obstacle == 2:
                        direction = self.get_last_image()
                        if direction in self.directions:
                            self.obstacle2_callback(direction)
                        else:
                            self.on_arrow_callback = self.obstacle2_callback
                            
                    elif self.num_obstacle == 3:
                        direction = self.directions[self.get_last_image()]
                        self.perform_carpark("L" if direction == "R" else "R")
                        self.pc.send("STITCH")
                    
                    with self.obstacle_lock:
                        if self.num_obstacle == 4:
                            logging.info(f"Timing: {(time_ns() - self.start_time) / 1e9:.3}s")
                        self.num_obstacle += 1
                elif stm_msg.startswith("ir"):
                    dist = stm_msg.split("ir")[1].replace("\n", "")
                    try:
                        dist = float(dist)
                    except:
                        logging.info(f"Couldn't cast WH dist {dist} to float")
                        continue 
                    self.wall_hug_length = dist
                elif stm_msg.startswith("us"):
                    stm_msg = stm_msg.replace("us", "").replace("\n", "")
                    dist = stm_msg.split(",")
                    try:
                        for i in range(2):
                            dist[i] = float(dist[i])
                    except:
                        logging.info(f"Couldn't cast US travelled dist {dist} to float")
                        continue
                    if self.num_obstacle == 1:
                        self.ultrasound_travelled_dist1 = dist[0]
                        self.ultrasound_stop_dist1 = dist[1]
                        logging.info(f"Set ultrasound_travelled_dist1 to {dist[0]} and ultrasound_stop_dist1 to {dist[1]}")
                    elif self.num_obstacle == 2:
                        self.ultrasound_travelled_dist2 = dist[0]
                        self.ultrasound_stop_dist2 = dist[1]
                        logging.info(f"Set ultrasound_travelled_dist2 to {dist[0]} and ultrasound_stop_dist2 to {dist[1]}")
                    
            except OSError as e:
                print(f"Error: {e}")
                continue
            
    def turn_and_go(self, full_length, half_width):
        """
        Returns (turn_degrees, distance)
        turn_degrees is positive for left, negative for right.
        """
        angle_rad = math.atan2(abs(half_width), full_length)
        angle_deg = math.degrees(angle_rad)
        distance = math.hypot(full_length, half_width)
        return abs(angle_deg), int(distance)

    def ultrasound_forward(self, distance_to_stop, send = True):
        cmd = f"FU{str(distance_to_stop)}"
        if send:
            self.stm.send(cmd + "\n")
        return cmd
        
    def perform_turn1(self, direction, send = True):
        opp_dir = "L" if direction == "R" else "R"
        cmd = "S" + direction + ",S"
        cmd += ",S" + opp_dir  + ",S"
        cmd += "," + self.ultrasound_forward(32, False)
        if send:
            self.stm.send(cmd + "\n")
        return cmd
        
    def wall_hug(self, direction, send = True):
        cmd = "FI" + direction
        if send:
            self.stm.send(cmd + "\n")
        return cmd
        
    def perform_turn2(self, direction, send = True):
        cmd = "F" + direction + "90"
        opp_dir = "L" if direction == "R" else "R"
        cmd += "," + self.wall_hug(opp_dir, False) + ",F2"
        # cmd += "," + "F" + opp_dir + "180,FI" + opp_dir + "O"
        cmd += "," + "F" + opp_dir + "90,F3,F" + opp_dir + "90" + ",FI" + opp_dir + "O"
        cmd += "," + self.wall_hug(opp_dir, False)
        cmd += "," + f"F{self.extra_dist}"
        
        if send:
            self.stm.send(cmd + "\n")
        return cmd
        
    def perform_carpark(self, direction, send = True):
        obs_1_to_2 = self.ultrasound_travelled_dist2 + self.ultrasound_stop_dist2 + self.slide_dist
        logging.info(f"Obs 1 to 2 dist: {obs_1_to_2}")
        logging.info(f"Obs 2 Length: {self.wall_hug_length}")
        full_length = self.chassis_length + self.ultrasound_travelled_dist1 + self.ultrasound_stop_dist1 \
            + obs_1_to_2
        logging.info(f"Estimated Length: {full_length}")
            
        half_width = ((self.wall_hug_length) / 2.0) + self.turn_bias + self.extra_dist + self.center_offset_diag
        logging.info(f"Estimated Width: {half_width}")
        
        if obs_1_to_2 > self.ninty_threshold_length or self.wall_hug_length < self.ninty_threshold_width:
            # do 90 90
            forward_dist = int(round(full_length - self.chassis_length - self.ninty_return_bias))
            opp_dir = "L" if direction == "R" else "R"
            if self.turn_x + self.turn_y > half_width - self.center_offset_ninty:
                back_dist = int(round(self.turn_x + self.turn_y - (half_width - self.center_offset_ninty)))
                if back_dist > 0: # if need to go back
                    cmd = f"F{direction}90,F{forward_dist},F{direction}90,R{back_dist},F{opp_dir}90," + self.ultrasound_forward(30, False)
                else: # perfect, dont go back
                    cmd = f"F{direction}90,F{forward_dist},F{direction}90,F{opp_dir}90," + self.ultrasound_forward(30, False)
            else: # no need go back
                turn_forward_dist = int(round(half_width - self.center_offset_diag - self.turn_x - self.turn_y))
                if turn_forward_dist == 0:
                    cmd = f"F{direction}90,F{forward_dist},F{direction}90,F{opp_dir}90," + self.ultrasound_forward(30, False)
                else:
                    cmd = f"F{direction}90,F{forward_dist},F{direction}90,F{turn_forward_dist},F{opp_dir}90," + self.ultrasound_forward(30, False)
            if send:
                self.stm.send(cmd + '\n')
            return cmd
        
        angle, _ = self.turn_and_go(full_length, half_width)
        
        cmd = "F" + direction + str(int(round(angle)) + 90) + "," + self.ultrasound_forward(25, False)
        if send:
            self.stm.send(cmd + '\n')
        return cmd
            
    def obstacle1_callback(self, direction):
        direction = self.directions[direction]
        logging.info(f"Calling obstacle 1 turn with direction {direction}")

        with self.lock:
            self.obstacle1_direction = direction

        self.perform_turn1(direction)
        
        self.on_arrow_callback = None
        
    def obstacle2_callback(self, direction):
        direction = self.directions[direction]

        logging.info(f"Calling obstacle 2 turn with direction {direction}")
        with self.lock:
            self.obstacle2_direction = direction
            
        self.perform_turn2(direction)
        self.on_arrow_callback = None
            
    def get_last_image(self) -> str:
        logging.info(f"Returning last_image as {self.last_image}")
        return self.last_image

    def set_last_image(self, img) -> None:
        with self.lock:
            self.last_image = img

        if self.on_arrow_callback and img in self.directions:
            self.on_arrow_callback(img)

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
        self.stm_thread.start()
        self.pc_thread.start()
        self.android_thread.start()
        # enter = input("Press Enter")
        # self.start_time = time_ns()
        # self.ultrasound_forward(24)
        
        self.stm_thread.join()
        self.pc_thread.join()
        self.android_thread.join()

        logging.info("Task 2 completed.")
        
if __name__ == "__main__":
    task1 = Task2()
    task1.start()
    

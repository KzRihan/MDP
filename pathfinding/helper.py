from pathfinding.consts import WIDTH, HEIGHT, Direction, MOVE_DIRECTION

# Default speed for motor commands (0-100, multiplied by 71 for PWM 0-7199)
DEFAULT_SPEED = 50

# Direction Values
# NORTH = 0 (up)
# EAST  = 2 (right)  
# SOUTH = 4 (down)
# WEST  = 6 (left)


def is_valid(center_x: int, center_y: int):
    """Checks if given position is within bounds

    Inputs
    ------
    center_x (int): x-coordinate
    center_y (int): y-coordinate

    Returns
    -------
    bool: True if valid, False otherwise
    """
    return center_x > 0 and center_y > 0 and center_x < WIDTH - 1 and center_y < HEIGHT - 1


# def command_generator(states, obstacles):
#     """
#     This function takes in a list of states and generates a list of commands for the robot to follow
    
#     Inputs
#     ------
#     states: list of State objects
#     obstacles: list of obstacles, each obstacle is a dictionary with keys "x", "y", "d", and "id"

#     Returns
#     -------
#     commands: list of commands for the robot to follow
#     """

#     # Convert the list of obstacles into a dictionary with key as the obstacle id and value as the obstacle
#     obstacles_dict = {ob['id']: ob for ob in obstacles}
    
#     # Initialize commands list
#     commands = []

#     # Iterate through each state in the list of states
#     for i in range(1, len(states)):
#         steps = "00"

#         # If previous state and current state are the same direction,
#         if states[i].direction == states[i - 1].direction:
#             # Forward - Must be (east facing AND x value increased) OR (north facing AND y value increased)
#             if (states[i].x > states[i - 1].x and states[i].direction == Direction.EAST) or (states[i].y > states[i - 1].y and states[i].direction == Direction.NORTH):
#                 commands.append("FW10")
#             # Forward - Must be (west facing AND x value decreased) OR (south facing AND y value decreased)
#             elif (states[i].x < states[i-1].x and states[i].direction == Direction.WEST) or (
#                     states[i].y < states[i-1].y and states[i].direction == Direction.SOUTH):
#                 commands.append("FW10")
#             # Backward - All other cases where the previous and current state is the same direction
#             else:
#                 commands.append("BW10")

#             # If any of these states has a valid screenshot ID, then add a SNAP command as well to take a picture
#             if states[i].screenshot_id != -1:
#                 # NORTH = 0
#                 # EAST = 2
#                 # SOUTH = 4
#                 # WEST = 6

#                 current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
#                 current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

#                 # Obstacle facing WEST, robot facing EAST
#                 if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
#                     if current_ob_dict['y'] > current_robot_position.y:
#                         commands.append(f"SNAP{states[i].screenshot_id}_L")
#                     elif current_ob_dict['y'] == current_robot_position.y:
#                         commands.append(f"SNAP{states[i].screenshot_id}_C")
#                     elif current_ob_dict['y'] < current_robot_position.y:
#                         commands.append(f"SNAP{states[i].screenshot_id}_R")
#                     else:
#                         commands.append(f"SNAP{states[i].screenshot_id}")
                
#                 # Obstacle facing EAST, robot facing WEST
#                 elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
#                     if current_ob_dict['y'] > current_robot_position.y:
#                         commands.append(f"SNAP{states[i].screenshot_id}_R")
#                     elif current_ob_dict['y'] == current_robot_position.y:
#                         commands.append(f"SNAP{states[i].screenshot_id}_C")
#                     elif current_ob_dict['y'] < current_robot_position.y:
#                         commands.append(f"SNAP{states[i].screenshot_id}_L")
#                     else:
#                         commands.append(f"SNAP{states[i].screenshot_id}")

#                 # Obstacle facing NORTH, robot facing SOUTH
#                 elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
#                     if current_ob_dict['x'] > current_robot_position.x:
#                         commands.append(f"SNAP{states[i].screenshot_id}_L")
#                     elif current_ob_dict['x'] == current_robot_position.x:
#                         commands.append(f"SNAP{states[i].screenshot_id}_C")
#                     elif current_ob_dict['x'] < current_robot_position.x:
#                         commands.append(f"SNAP{states[i].screenshot_id}_R")
#                     else:
#                         commands.append(f"SNAP{states[i].screenshot_id}")

#                 # Obstacle facing SOUTH, robot facing NORTH
#                 elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
#                     if current_ob_dict['x'] > current_robot_position.x:
#                         commands.append(f"SNAP{states[i].screenshot_id}_R")
#                     elif current_ob_dict['x'] == current_robot_position.x:
#                         commands.append(f"SNAP{states[i].screenshot_id}_C")
#                     elif current_ob_dict['x'] < current_robot_position.x:
#                         commands.append(f"SNAP{states[i].screenshot_id}_L")
#                     else:
#                         commands.append(f"SNAP{states[i].screenshot_id}")
#             continue

#         # If previous state and current state are not the same direction, it means that there will be a turn command involved
#         # Assume there are 4 turning command: FR, FL, BL, BR (the turn command will turn the robot 90 degrees)
#         # FR00 | FR30: Forward Right;
#         # FL00 | FL30: Forward Left;
#         # BR00 | BR30: Backward Right;
#         # BL00 | BL30: Backward Left;

#         # Facing north previously
#         if states[i - 1].direction == Direction.NORTH:
#             # Facing east afterwards
#             if states[i].direction == Direction.EAST:
#                 # y value increased -> Forward Right
#                 if states[i].y > states[i - 1].y:
#                     commands.append("FR{}".format(steps))
#                 # y value decreased -> Backward Left
#                 else:
#                     commands.append("BL{}".format(steps))
#             # Facing west afterwards
#             elif states[i].direction == Direction.WEST:
#                 # y value increased -> Forward Left
#                 if states[i].y > states[i - 1].y:
#                     commands.append("FL{}".format(steps))
#                 # y value decreased -> Backward Right
#                 else:
#                     commands.append("BR{}".format(steps))
#             else:
#                 raise Exception("Invalid turing direction")

#         elif states[i - 1].direction == Direction.EAST:
#             if states[i].direction == Direction.NORTH:
#                 if states[i].y > states[i - 1].y:
#                     commands.append("FL{}".format(steps))
#                 else:
#                     commands.append("BR{}".format(steps))

#             elif states[i].direction == Direction.SOUTH:
#                 if states[i].y > states[i - 1].y:
#                     commands.append("BL{}".format(steps))
#                 else:
#                     commands.append("FR{}".format(steps))
#             else:
#                 raise Exception("Invalid turing direction")

#         elif states[i - 1].direction == Direction.SOUTH:
#             if states[i].direction == Direction.EAST:
#                 if states[i].y > states[i - 1].y:
#                     commands.append("BR{}".format(steps))
#                 else:
#                     commands.append("FL{}".format(steps))
#             elif states[i].direction == Direction.WEST:
#                 if states[i].y > states[i - 1].y:
#                     commands.append("BL{}".format(steps))
#                 else:
#                     commands.append("FR{}".format(steps))
#             else:
#                 raise Exception("Invalid turing direction")

#         elif states[i - 1].direction == Direction.WEST:
#             if states[i].direction == Direction.NORTH:
#                 if states[i].y > states[i - 1].y:
#                     commands.append("FR{}".format(steps))
#                 else:
#                     commands.append("BL{}".format(steps))
#             elif states[i].direction == Direction.SOUTH:
#                 if states[i].y > states[i - 1].y:
#                     commands.append("BR{}".format(steps))
#                 else:
#                     commands.append("FL{}".format(steps))
#             else:
#                 raise Exception("Invalid turing direction")
#         else:
#             raise Exception("Invalid position")

#         # If any of these states has a valid screenshot ID, then add a SNAP command as well to take a picture
#         if states[i].screenshot_id != -1:  
#             # NORTH = 0
#             # EAST = 2
#             # SOUTH = 4
#             # WEST = 6

#             current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
#             current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

#             # Obstacle facing WEST, robot facing EAST
#             if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
#                 if current_ob_dict['y'] > current_robot_position.y:
#                     commands.append(f"SNAP{states[i].screenshot_id}_L")
#                 elif current_ob_dict['y'] == current_robot_position.y:
#                     commands.append(f"SNAP{states[i].screenshot_id}_C")
#                 elif current_ob_dict['y'] < current_robot_position.y:
#                     commands.append(f"SNAP{states[i].screenshot_id}_R")
#                 else:
#                     commands.append(f"SNAP{states[i].screenshot_id}")
            
#             # Obstacle facing EAST, robot facing WEST
#             elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
#                 if current_ob_dict['y'] > current_robot_position.y:
#                     commands.append(f"SNAP{states[i].screenshot_id}_R")
#                 elif current_ob_dict['y'] == current_robot_position.y:
#                     commands.append(f"SNAP{states[i].screenshot_id}_C")
#                 elif current_ob_dict['y'] < current_robot_position.y:
#                     commands.append(f"SNAP{states[i].screenshot_id}_L")
#                 else:
#                     commands.append(f"SNAP{states[i].screenshot_id}")

#             # Obstacle facing NORTH, robot facing SOUTH
#             elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
#                 if current_ob_dict['x'] > current_robot_position.x:
#                     commands.append(f"SNAP{states[i].screenshot_id}_L")
#                 elif current_ob_dict['x'] == current_robot_position.x:
#                     commands.append(f"SNAP{states[i].screenshot_id}_C")
#                 elif current_ob_dict['x'] < current_robot_position.x:
#                     commands.append(f"SNAP{states[i].screenshot_id}_R")
#                 else:
#                     commands.append(f"SNAP{states[i].screenshot_id}")

#             # Obstacle facing SOUTH, robot facing NORTH
#             elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
#                 if current_ob_dict['x'] > current_robot_position.x:
#                     commands.append(f"SNAP{states[i].screenshot_id}_R")
#                 elif current_ob_dict['x'] == current_robot_position.x:
#                     commands.append(f"SNAP{states[i].screenshot_id}_C")
#                 elif current_ob_dict['x'] < current_robot_position.x:
#                     commands.append(f"SNAP{states[i].screenshot_id}_L")
#                 else:
#                     commands.append(f"SNAP{states[i].screenshot_id}")

#     # Final command is the stop command (FIN)
#     commands.append("FIN")  

#     # Compress commands if there are consecutive forward or backward commands
#     compressed_commands = [commands[0]]

#     for i in range(1, len(commands)):
#         # If both commands are BW
#         if commands[i].startswith("BW") and compressed_commands[-1].startswith("BW"):
#             # Get the number of steps of previous command
#             steps = int(compressed_commands[-1][2:])
#             # If steps are not 90, add 10 to the steps
#             if steps != 90:
#                 compressed_commands[-1] = "BW{}".format(steps + 10)
#                 continue

#         # If both commands are FW
#         elif commands[i].startswith("FW") and compressed_commands[-1].startswith("FW"):
#             # Get the number of steps of previous command
#             steps = int(compressed_commands[-1][2:])
#             # If steps are not 90, add 10 to the steps
#             if steps != 90:
#                 compressed_commands[-1] = "FW{}".format(steps + 10)
#                 continue
        
#         # Otherwise, just add as usual
#         compressed_commands.append(commands[i])
#     time = time_generator(compressed_commands)
#     return compressed_commands,time

def _get_snap_command(screenshot_id: int, obstacle: dict, robot_position) -> str:
    """Generate SNAP command with direction suffix based on obstacle and robot positions.
    
    Args:
        screenshot_id: ID of the obstacle to photograph
        obstacle: Dict with obstacle info {'x', 'y', 'd', 'id'}
        robot_position: Current robot state with x, y, direction
    
    Returns:
        SNAP command string like 'SNAP1_L', 'SNAP1_C', or 'SNAP1_R'
    """
    ob_d = obstacle['d']
    robot_d = robot_position.direction
    
    # Mapping: (obstacle_direction, robot_direction) -> (compare_attr, left_cond, right_cond)
    # left_cond/right_cond: True if obstacle coord > robot coord means L/R respectively
    direction_map = {
        (6, 2): ('y', True, False),   # Obstacle WEST, robot EAST
        (2, 6): ('y', False, True),   # Obstacle EAST, robot WEST
        (0, 4): ('x', True, False),   # Obstacle NORTH, robot SOUTH
        (4, 0): ('x', False, True),   # Obstacle SOUTH, robot NORTH
    }
    
    key = (ob_d, int(robot_d))
    if key not in direction_map:
        return f"SNAP{screenshot_id}"
    
    attr, left_when_greater, right_when_greater = direction_map[key]
    ob_val = obstacle[attr]
    robot_val = getattr(robot_position, attr)
    
    if ob_val == robot_val:
        return f"SNAP{screenshot_id}_C"
    elif ob_val > robot_val:
        suffix = '_L' if left_when_greater else '_R'
    else:
        suffix = '_R' if left_when_greater else '_L'
    
    return f"SNAP{screenshot_id}{suffix}"


def command_generator(states, obstacles, speed=None):
    """
    Generate movement + turn + SNAP commands for the robot using new motor protocol.
    
    Args:
        states: List of State objects representing robot path
        obstacles: List of obstacles, each a dict with keys 'x', 'y', 'd', 'id'
        speed: Motor speed (0-100). If None, uses DEFAULT_SPEED
        
    Returns:
        Tuple of (commands, time_list) where commands are motor protocol strings
    """

    obstacles_dict = {ob['id']: ob for ob in obstacles}
    motor_speed = speed if speed is not None else DEFAULT_SPEED
    commands = []
    cmd_id = 1

    for i in range(1, len(states)):
        prev = states[i - 1]
        curr = states[i]

        dx = curr.x - prev.x
        dy = curr.y - prev.y
        old_dir = int(prev.direction)
        new_dir = int(curr.direction)
        diff = (new_dir - old_dir) % 8

        # === Case 1: Straight movement (same direction) ===
        if curr.direction == prev.direction:
            # Get the canonical (dx, dy) for this direction
            expected_dx, expected_dy, _ = MOVE_DIRECTION[int(curr.direction)]

            if (dx, dy) == (expected_dx, expected_dy):
                # Forward movement
                commands.append(f":{cmd_id}/MOTOR/FWD/{motor_speed}/10;")
                cmd_id += 1
            elif (dx, dy) == (-expected_dx, -expected_dy):
                # Backward movement
                commands.append(f":{cmd_id}/MOTOR/REV/{motor_speed}/10;")
                cmd_id += 1
            else:
                raise Exception(
                    f"Unexpected straight movement: dir={curr.direction}, "
                    f"expected ({expected_dx},{expected_dy}) or opposite, got ({dx},{dy})"
                )
                
        # === Case 2: 45° Diagonal Turns ===
        elif diff == 1:   # +45° clockwise
            expected_dx, expected_dy, _ = MOVE_DIRECTION[int(curr.direction)]
            new_dx, new_dy = expected_dx * dx, expected_dy * dy
            if new_dx > 0 or new_dy > 0:
                # Forward right 45
                commands.append(f":{cmd_id}/MOTOR/TURNR/{motor_speed}/45;")
                cmd_id += 1
            else:
                # Backward left 45
                commands.append(f":{cmd_id}/MOTOR/REVTURNL/{motor_speed}/45;")
                cmd_id += 1
        elif diff == 7:  # -45° counter-clockwise
            expected_dx, expected_dy, _ = MOVE_DIRECTION[int(curr.direction)]
            new_dx, new_dy = expected_dx * dx, expected_dy * dy
            if new_dx > 0 or new_dy > 0:
                # Forward left 45
                commands.append(f":{cmd_id}/MOTOR/TURNL/{motor_speed}/45;")
                cmd_id += 1
            else:
                # Backward right 45
                commands.append(f":{cmd_id}/MOTOR/REVTURNR/{motor_speed}/45;")
                cmd_id += 1

        # === Case 3: 90° Turns ===
        elif diff == 2:  # clockwise (FR90 or BL90)
            expected_dx, expected_dy, _ = MOVE_DIRECTION[int(curr.direction)]
            new_dx, new_dy = expected_dx * dx, expected_dy * dy
            if new_dx > 0 or new_dy > 0:
                # Forward right 90
                commands.append(f":{cmd_id}/MOTOR/TURNR/{motor_speed}/90;")
                cmd_id += 1
            else:
                # Backward left 90 (reverse turn left)
                commands.append(f":{cmd_id}/MOTOR/REVTURNL/{motor_speed}/90;")
                cmd_id += 1
        elif diff == 6:  # counter-clockwise (FL90 or BR90)
            expected_dx, expected_dy, _ = MOVE_DIRECTION[int(curr.direction)]
            new_dx, new_dy = expected_dx * dx, expected_dy * dy
            if new_dx > 0 or new_dy > 0:
                # Forward left 90
                commands.append(f":{cmd_id}/MOTOR/TURNL/{motor_speed}/90;")
                cmd_id += 1
            else:
                # Backward right 90 (reverse turn right)
                commands.append(f":{cmd_id}/MOTOR/REVTURNR/{motor_speed}/90;")
                cmd_id += 1

        # === Case 4: 180° Turn ===
        elif diff == 4:
            # Two 90-degree right turns
            commands.append(f":{cmd_id}/MOTOR/TURNR/{motor_speed}/90;")
            cmd_id += 1
            commands.append(f":{cmd_id}/MOTOR/TURNR/{motor_speed}/90;")
            cmd_id += 1

        else:
            raise Exception(f"Unexpected turn diff: {diff} from {old_dir} -> {new_dir}")

        # === Case 5: SNAP command for taking pictures ===
        if curr.screenshot_id != -1:
            snap_cmd = _get_snap_command(
                curr.screenshot_id,
                obstacles_dict[curr.screenshot_id],
                curr
            )
            commands.append(snap_cmd)

    # Final stop command
    commands.append(f":{cmd_id}/MOTOR/STOP/0/0;")
    cmd_id += 1
    commands.append("FIN")  # Keep FIN marker for higher-level processing

    # === Compress consecutive FWD/REV commands ===
    compressed = [commands[0]]
    for i in range(1, len(commands)):
        # Check if both are forward commands
        if "/MOTOR/FWD/" in commands[i] and "/MOTOR/FWD/" in compressed[-1]:
            # Extract distance from previous command
            parts = compressed[-1].split("/")
            distance = int(parts[-1].rstrip(";"))
            # Add 10 to distance if not at max
            if distance < 180:
                parts[-1] = f"{distance + 10};"
                compressed[-1] = "/".join(parts)
                continue
        # Check if both are reverse commands
        elif "/MOTOR/REV/" in commands[i] and "/MOTOR/REV/" in compressed[-1]:
            # Extract distance from previous command
            parts = compressed[-1].split("/")
            distance = int(parts[-1].rstrip(";"))
            # Add 10 to distance if not at max
            if distance < 180:
                parts[-1] = f"{distance + 10};"
                compressed[-1] = "/".join(parts)
                continue
        compressed.append(commands[i])

    # Renumber command IDs to be sequential after compression
    final_commands = []
    motor_cmd_id = 1
    for cmd in compressed:
        if cmd.startswith(":"):  # Motor protocol command
            # Extract command parts and replace ID
            parts = cmd.split("/")
            parts[0] = f":{motor_cmd_id}"
            final_commands.append("/".join(parts))
            motor_cmd_id += 1
        else:
            # SNAP, FIN, or other non-motor commands
            final_commands.append(cmd)
    
    time = time_generator(final_commands)
    return final_commands, time




# def time_generator(compressed_commands: list):
#     """
#     This function takes in a list of commands and generates the time taken

#     Inputs
#     ------
#     compressed_commands: list of commands 

#     Returns
#     -------
#     time: list of time taken for each command
#     """
#     time = []
    
#     # Iterate through each command in the list of compressed commands
#     for command in compressed_commands:
#         # Check if the command starts with 'FW' (forward movement) or 'BW' (backward movement)
#         if command.startswith("FW") or command.startswith("BW"):
#             # Extract the number of steps from the command string
#             steps = int(command[2:])
#             # Calculate time for movement: 3 seconds per step
#             time.append(steps / 10 * 3)
#         # Check if the command is a turning command (FR, FL, BR, BL)
#         elif command.startswith("FR") or command.startswith("FL") or command.startswith("BR") or command.startswith("BL"):
#             # A turn takes 8 seconds, 
#             time.append(8)
#         # Handle 'SNAP' command for taking a picture
#         elif command.startswith("SNAP"):
#             # (We assume) taking a picture takes 0 second (but we filter this out later anyway, if not we can just add x seconds to the latest step)
#             #time[:-1] += 1
#             time.append(0)
#         # Handle 'FIN' command to stop
#         elif command.startswith("FIN"):
#             # Final Commands just to end simulation should take 0 seconds
#             time.append(0)
    
#     return time


def time_generator(compressed_commands: list):
    """
    This function takes in a list of commands and generates the time taken.
    Handles both new motor protocol commands and legacy SNAP/FIN commands.

    Inputs
    ------
    compressed_commands: list of commands in motor protocol format

    Returns
    -------
    time: list of time taken for each command
    """
    time = []
    
    for command in compressed_commands:
        # Motor protocol commands (format: :cmdId/MOTOR/action/speed/param;)
        if command.startswith(":"):
            parts = command.split("/")
            if len(parts) >= 4:
                action = parts[2]
                param = int(parts[-1].rstrip(";"))
                
                if action == "FWD" or action == "REV":
                    # Forward/Reverse: param is distance in units
                    # 3 seconds per 10-unit step
                    time.append(param / 10 * 3)
                
                elif action in ["TURNR", "TURNL", "REVTURNR", "REVTURNL"]:
                    # Turn commands: param is angle in degrees
                    if param == 45:
                        time.append(4)  # 45-degree turn
                    elif param == 90:
                        time.append(8)  # 90-degree turn
                    else:
                        # Estimate time based on angle (8 seconds for 90 degrees)
                        time.append(param / 90 * 8)
                
                elif action == "STOP":
                    time.append(0)  # Stop command takes no time
                
                else:
                    # Unknown motor action, default to 0
                    time.append(0)
            else:
                # Malformed command, default to 0
                time.append(0)
        
        # Legacy SNAP command for picture taking
        elif command.startswith("SNAP"):
            time.append(0)
        
        # Legacy FIN command
        elif command.startswith("FIN"):
            time.append(0)
        
        else:
            # Unknown command type
            print(f"Warning: Unknown command in time_generator: {command}")
            time.append(0)
    
    return time

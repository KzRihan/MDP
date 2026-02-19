from enum import Enum

class Direction(int, Enum):
    """Robot direction values.
    Main cardinals: NORTH=0 (up), EAST=2 (right), SOUTH=4 (down), WEST=6 (left)
    Diagonals: NORTHEAST=1, SOUTHEAST=3, SOUTHWEST=5, NORTHWEST=7
    """
    NORTH = 0      # up
    NORTHEAST = 1
    EAST = 2       # right
    SOUTHEAST = 3
    SOUTH = 4      # down
    SOUTHWEST = 5
    WEST = 6       # left
    NORTHWEST = 7
    SKIP = 8

    def __int__(self):
        return self.value

    @staticmethod
    def rotation_cost(d1, d2):
        diff = abs(d1 - d2)
        return min(diff, 8 - diff)

MOVE_DIRECTION = [
    (0, 1, Direction.NORTH),
    (1, 1, Direction.NORTHEAST),
    (1, 0, Direction.EAST),
    (1, -1, Direction.SOUTHEAST),
    (0, -1, Direction.SOUTH),
    (-1, -1, Direction.SOUTHWEST),
    (-1, 0, Direction.WEST),
    (-1, 1, Direction.NORTHWEST),
]

TURN_FACTOR = 1

EXPANDED_CELL = 1 # for both agent and obstacles

WIDTH = 20
HEIGHT = 20

ITERATIONS = 2000
TURN_RADIUS = 1

SAFE_COST = 1000 # the cost for the turn in case there is a chance that the robot is touch some obstacle
SCREENSHOT_COST = 50 # the cost for the place where the picture is taken
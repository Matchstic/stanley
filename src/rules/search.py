from .base import BaseRule
import enum
from constants import YAW_RATE

class Direction(enum.Enum):
    NONE  = -1
    LEFT  = 0
    RIGHT = 1

class SearchRule(BaseRule):
    '''
    Rule to yaw in the direction a detection was last seen in
    '''

    hasSeenPerson = False
    personDirection = Direction.NONE

    def isActive(self):
        return self.hasSeenPerson

    def update(self):
        detection = self.camera.closestDetection()

        if detection != None:
            if detection.x < 0:
                self.personDirection = Direction.LEFT
            elif detection.x > 0:
                self.personDirection = Direction.RIGHT
            else:
                self.personDirection = Direction.NONE

            self.hasSeenPerson = True

        # Yaw in that saved direction
        if self.personDirection is Direction.NONE:
            self._targetYaw = 0.0
        else:
            self._targetYaw = float((0.0 - YAW_RATE) if self.personDirection is Direction.LEFT else YAW_RATE)

    def reset(self):
        super().reset()

        self.hasSeenPerson = False
        self.personDirection = Direction.NONE

    def name(self) -> str:
        return 'search'
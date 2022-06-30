from .base import BaseRule
import math
from constants import MINIMUM_DISTANCE, YAW_MAX_DAMP

class FollowRule(BaseRule):
    '''
    Rule to follow a detected person
    '''

    def isActive(self):
        return self.camera.closestDetection() != None

    def update(self):
        detection = self.camera.closestDetection()
        if detection == None:
            return

        # Correctly re-project the xDistance etc accounting for minimum distance

        xDistance = detection.x
        zDistance = detection.z
        heading = self.headingChange(xDistance, zDistance)

        hypotenuse = self.findHypotenuse(abs(heading), abs(detection.z)) - MINIMUM_DISTANCE

        if hypotenuse > 0:
            xDistance = math.sin(math.radians(abs(heading))) * hypotenuse
            zDistance = math.cos(math.radians(abs(heading))) * hypotenuse

            # Handle direction
            xDistance = xDistance * (1 if detection.x >= 0 else -1)
            zDistance = zDistance * (1 if detection.z >= 0 else -1)
        elif hypotenuse == 0:
            xDistance = 0
            zDistance = 0
        else:
            xDistance = math.sin(math.radians(abs(heading))) * hypotenuse
            zDistance = math.cos(math.radians(abs(heading))) * hypotenuse

            # Handle direction
            xDistance = xDistance * (1 if detection.x >= 0 else -1)
            zDistance = zDistance * (1 if detection.z >= 0 else -1)

        self._targetPosition = (zDistance, xDistance)

        # Apply damping to avoid oscillations
        yawDamp = ((1.0 - YAW_MAX_DAMP) * math.pow(abs(detection.x), 2)) + YAW_MAX_DAMP if abs(detection.x) <= 1.0 else 1.0
        self._targetYaw = heading / yawDamp

    def headingChange(self, xDistance, zDistance):
        # Safeguard against weirdness in detection data
        if zDistance == 0: return 0

        isLeftward = xDistance < 0

        changeRadians = math.atan(abs(xDistance) / zDistance)
        changeDegrees = math.degrees(changeRadians)

        return float((0.0 - changeDegrees) if isLeftward == True else changeDegrees)

    def findHypotenuse(self, angle, zDistance):
        return math.cos(math.radians(angle)) * zDistance

    def reset(self):
        super().reset()

    def name(self) -> str:
        return 'follow'
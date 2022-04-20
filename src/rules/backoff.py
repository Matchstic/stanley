from .base import BaseRule
from constants import BACKOFF_DISTANCE, MINIMUM_DISTANCE

class BackoffRule(BaseRule):
    '''
    Rule to move back if the detection is too close
    '''

    def isActive(self):
        return self.camera.closestDetection() != None and \
            self.camera.closestDetection().z < BACKOFF_DISTANCE

    def update(self):
        detection = self.camera.closestDetection()
        if detection == None:
            return

        xDistance = detection.x
        zDistance = detection.z

        self._targetPosition = (zDistance - MINIMUM_DISTANCE, xDistance)

    def name(self) -> str:
        return 'backoff'
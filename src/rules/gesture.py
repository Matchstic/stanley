from .base import BaseRule
from ..gestures.manager import GestureManager

class GestureRule(BaseRule):
    '''
    Rule to run gesture-based command if observed by underlying system
    '''

    gestureManager: GestureManager = None

    def __init__(self, vehicle, camera, gestureManager: GestureManager):
        BaseRule.__init__(self, vehicle, camera)
        self.gestureManager = gestureManager

    def isActive(self):
        return False

    def update(self):
        # If gesture is currently detected by system, then spawn its control set as
        # a new thread managed by this rule. Active state is equal to whether the thread is
        # running.
        pass

    def ruleHandlesControl(self) -> bool:
        return True

    def name(self) -> str:
        return 'gesture'
from .base import BaseRule

class NoDetectionRule(BaseRule):
    '''
    Rule to just sit in the same position without yaw, waiting for initial
    detection
    '''

    def isActive(self):
        return True

    def name(self) -> str:
        return 'none'
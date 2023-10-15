from .base import BaseRule

class GestureRule(BaseRule):
    '''
    Rule to run gesture-based command if observed by underlying system
    '''

    _runningGestureThread = None

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
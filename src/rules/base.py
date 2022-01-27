class BaseRule:

    vehicle = None
    camera = None

    _targetPosition = (0, 0)
    _targetYaw      = 0

    def __init__(self, vehicle, camera):
        self.vehicle = vehicle
        self.camera = camera

    def active(self):
        return False

    def update(self):
        self._targetPosition = (0, 0)
        self._targetYaw = 0

    def reset(self):
        self._targetPosition = (0, 0)
        self._targetYaw = 0

    def getState(self):
        return (self._targetPosition, self._targetYaw)

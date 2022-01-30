from typing import Tuple

class BaseRule:

    vehicle = None
    camera = None

    _targetPosition = (0.0, 0.0)
    _targetYaw      = 0.0

    def __init__(self, vehicle, camera):
        self.vehicle = vehicle
        self.camera = camera

    def isActive(self) -> bool:
        return False

    def update(self) -> None:
        self._targetPosition = (0.0, 0.0)
        self._targetYaw = 0.0

    def reset(self) -> None:
        self._targetPosition = (0.0, 0.0)
        self._targetYaw = 0.0

    def getState(self) -> Tuple[Tuple[float, float], float]:
        return (self._targetPosition, self._targetYaw)

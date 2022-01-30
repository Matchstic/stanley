from enum import Enum
from constants import ALTITUDE, HEARTBEAT_TIMEOUT, ALTITUDE_FUZZINESS
from .rules import LostDetection, NoDetection, base
from commands import setPositionTarget, clearROI
from dronekit import Vehicle

class ExecutionState(Enum):
    Init          = 0
    AwaitingReady = 1
    Running       = 2
    ModeChanged   = 3
    Stop          = 4

class Core:

    vehicle: Vehicle = None
    camera = None
    state: ExecutionState = ExecutionState.Init
    rules: list[base.BaseRule] = []

    def __init__(self, vehicle: Vehicle, camera):
        self.camera = camera
        self.vehicle = vehicle

        # Setup vehicle etc
        self.vehicle.add_attribute_listener('mode', self.modeCallback)
        self.vehicle.add_attribute_listener('armed', self.armedCallback)
        self.vehicle.add_attribute_listener('last_heartbeat', self.lastHeartbeatCallback)

        # Setup rules in heirarchy order
        self.rules.append(LostDetection(self.vehicle, self.camera))
        self.rules.append(NoDetection(self.vehicle, self.camera))

        # Enter ready state
        self.state = ExecutionState.AwaitingReady

    #### Callbacks

    def modeCallback(self, _) -> None:
        print("Vehicle mode %s" % (self.vehicle.mode,))

        if not self.isReady() and self.state != ExecutionState.Init:
            self.state = ExecutionState.ModeChanged

    def armedCallback(self, _) -> None:
        print("Vehicle armed %d" % (self.vehicle.armed,))

        if not self.isReady() and self.state != ExecutionState.Init:
            self.state = ExecutionState.ModeChanged

    def lastHeartbeatCallback(self, _) -> None:
        if not self.isConnected() and self.state != ExecutionState.Init:
            self.state = ExecutionState.ModeChanged

    #### Getters

    def isReady(self) -> bool:
        return self.vehicle.armed and \
                self.vehicle.mode.name == 'GUIDED' and \
                self.vehicle.location.global_relative_frame.alt - ALTITUDE_FUZZINESS >= ALTITUDE

    def isConnected(self) -> bool:
        return self.vehicle.last_heartbeat < HEARTBEAT_TIMEOUT

    #### State machine

    def run(self) -> None:
        while not self.state is ExecutionState.Stop:
            # Get camera data?

            if self.state is ExecutionState.Init:
                # Do nothing during setup.
                pass
            elif self.state is ExecutionState.AwaitingReady:

                if self.isReady() and self.isConnected():
                    self.state = ExecutionState.Running

            elif self.state is ExecutionState.Running:

                # Update each rule with new data
                for rule in self.rules:
                    rule.update()

                # Get the highest active rule's output
                state = ((0.0, 0.0), 0.0)
                for rule in self.rules:
                    if rule.isActive():
                        state = rule.getState()
                        break

                # Apply local translation and yaw differential
                position, yaw = state
                setPositionTarget(self.vehicle, position, yaw)

            elif self.state is ExecutionState.ModeChanged:

                # Reset rules
                for rule in self.rules:
                    rule.reset()

                # Clear any guided state remaining
                clearROI(self.vehicle)

                self.state = ExecutionState.AwaitingReady

    def stop(self) -> None:
        self.state = ExecutionState.Stop

        # Cleanup
        self.vehicle.close()
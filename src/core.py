import time

from enum import Enum
from constants import ALTITUDE, HEARTBEAT_TIMEOUT, ALTITUDE_FUZZINESS

from commands import clearROI, setPositionTarget
from dronekit import Vehicle
from camera.base import BaseCamera

from rules.base import BaseRule
from rules.none import NoDetectionRule
from rules.search import SearchRule

class ExecutionState(Enum):
    Init           = 0
    AwaitingArm    = 1
    Takeoff        = 2
    AwaitingReady  = 3
    Running        = 4
    PilotOnly      = 5
    ConnectionLoss = 6
    Stop           = 7

class Core:

    vehicle: Vehicle = None
    camera: BaseCamera = None
    state: ExecutionState = ExecutionState.Init
    rules: list[BaseRule] = []

    def __init__(self, vehicle: Vehicle, camera: BaseCamera):
        self.camera = camera
        self.vehicle = vehicle

        # Setup vehicle etc
        self.vehicle.add_attribute_listener('mode', self.modeCallback)
        self.vehicle.add_attribute_listener('armed', self.armedCallback)
        self.vehicle.add_attribute_listener('last_heartbeat', self.lastHeartbeatCallback)

        # Setup rules in heirarchy order
        self.rules.append(SearchRule(self.vehicle, self.camera))
        self.rules.append(NoDetectionRule(self.vehicle, self.camera))

        # Enter ready state
        self.state = ExecutionState.AwaitingArm

    #### Callbacks

    def modeCallback(self, _) -> None:
        print("Vehicle mode %s" % (self.vehicle.mode,))

        if self.vehicle.mode.name != "GUIDED" and self.state == ExecutionState.Running:
            self.state = ExecutionState.PilotOnly

    def armedCallback(self, _) -> None:
        print("Vehicle armed %d" % (self.vehicle.armed,))

        if not self.vehicle.armed and self.state != ExecutionState.Init:
            self.state = ExecutionState.AwaitingArm

    def lastHeartbeatCallback(self, _) -> None:
        if not self.isConnected() and self.state != ExecutionState.Init:
            self.state = ExecutionState.ConnectionLoss

    #### Getters

    def isReady(self) -> bool:
        return self.vehicle.armed and \
                self.vehicle.mode.name == 'GUIDED' and \
                self.vehicle.location.global_relative_frame.alt > 0.5 # Indicates we are actually flying

    def isAltitudeOk(self) -> bool:
        return self.vehicle.location.global_relative_frame.alt - ALTITUDE_FUZZINESS >= ALTITUDE

    def isConnected(self) -> bool:
        return self.vehicle.last_heartbeat < HEARTBEAT_TIMEOUT

    def armable(self) -> bool:
        return not self.vehicle.armed and \
                self.vehicle.is_armable and \
                self.vehicle.mode.name == 'GUIDED'

    #### State machine

    def run(self) -> None:
        while not self.state is ExecutionState.Stop:

            if self.state is ExecutionState.Init:
                # Do nothing during setup.
                pass
            elif self.state is ExecutionState.AwaitingArm:

                if self.armable():
                    time.sleep(5) # safety delay
                    self.state = ExecutionState.Takeoff

            elif self.state is ExecutionState.Takeoff:

                # Takeoff and wait until we hit altitude
                self.vehicle.armed = True

                # Confirm vehicle armed before attempting to take off
                while not self.vehicle.armed:
                    print('Waiting for arming...')
                    time.sleep(1)

                print('Take off to ' + str(ALTITUDE) + 'm')
                self.vehicle.simple_takeoff(ALTITUDE)

                # Wait until the vehicle reaches altitude
                self.state = ExecutionState.AwaitingReady

            elif self.state is ExecutionState.AwaitingReady:

                if self.isReady() and self.isConnected() and self.isAltitudeOk():
                    # Prepare for running by resetting rules
                    for rule in self.rules:
                        rule.reset()

                    # And, clear any guided state remaining from a previous run
                    clearROI(self.vehicle)

                    self.state = ExecutionState.Running

                # Shouldn't really happen, but here just in case!
                elif self.vehicle.mode.name != 'GUIDED':
                    self.state = ExecutionState.PilotOnly

            elif self.state is ExecutionState.Running:
                # Mode and armed callbacks handle exiting this state.

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

            elif self.state is ExecutionState.ConnectionLoss:
                # until reconnected, nothing we can do.
                time.sleep(0.1)
                pass

            elif self.state is ExecutionState.PilotOnly:
                # Pilot is in control. Do nothing until we have disarmed again.
                time.sleep(0.1)
                pass

    def stop(self) -> None:
        self.state = ExecutionState.Stop

        # Cleanup
        self.vehicle.close()
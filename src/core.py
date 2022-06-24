import time

from enum import Enum
from constants import ALTITUDE, HEARTBEAT_TIMEOUT, ALTITUDE_FUZZINESS

from commands import setPositionTarget
from dronekit import Vehicle, VehicleMode
from camera.base import BaseCamera

from rules.base import BaseRule
from rules.none import NoDetectionRule
from rules.search import SearchRule
from rules.follow import FollowRule
from rules.backoff import BackoffRule

class ExecutionState(str, Enum):
    Init           = "INIT"
    AwaitingArm    = "AWAITING_ARM"
    Takeoff        = "TAKEOFF"
    AwaitingReady  = "AWAITING_READY"
    Running        = "RUNNING"
    PilotOnly      = "PILOT_ONLY"
    ConnectionLoss = "CONNECTION_LOSS"
    Stop           = "STOP"

class Core:

    vehicle: Vehicle = None
    camera: BaseCamera = None
    state: ExecutionState = ExecutionState.Init
    rules: list[BaseRule] = []

    activeRule = 'n/a'

    def __init__(self, vehicle: Vehicle, camera: BaseCamera):
        self.camera = camera
        self.vehicle = vehicle

        # Setup vehicle etc
        self.vehicle.add_attribute_listener('mode', self.modeCallback)
        self.vehicle.add_attribute_listener('armed', self.armedCallback)
        self.vehicle.add_attribute_listener('last_heartbeat', self.lastHeartbeatCallback)

        # Setup rules in heirarchy order
        self.rules.append(BackoffRule(self.vehicle, self.camera))
        self.rules.append(FollowRule(self.vehicle, self.camera))
        self.rules.append(SearchRule(self.vehicle, self.camera))
        self.rules.append(NoDetectionRule(self.vehicle, self.camera))

        # Enter ready state
        self.state = ExecutionState.AwaitingArm

    #### Callbacks

    def modeCallback(self, _, _1, _2) -> None:
        print("Vehicle mode %s" % (self.vehicle.mode,))

        if self.vehicle.mode.name != "GUIDED" and self.state not in [ExecutionState.Init, ExecutionState.ConnectionLoss, ExecutionState.Stop]:
            self.state = ExecutionState.PilotOnly
        elif self.vehicle.mode.name == "GUIDED":
            if self.isReady() and self.isConnected():
                # Go into loiter mode because this is totally undefined now
                # The pilot needs to set the vehicle down and then switch back into GUIDED
                print('Cannot restart core flow due to being airborne!')
                setPositionTarget(self.vehicle, (0,0), 0)
                return

            if self.vehicle.armed:
                self.vehicle.disarm()

            self.state = ExecutionState.AwaitingArm

    def armedCallback(self, _, _1, _2) -> None:
        print("Vehicle armed %d" % (self.vehicle.armed,))

        if not self.vehicle.armed and self.state != ExecutionState.Init:
            self.state = ExecutionState.AwaitingArm

    def lastHeartbeatCallback(self, _, _1, _2) -> None:
        if not self.isConnected() and self.state != ExecutionState.Init:
            self.state = ExecutionState.ConnectionLoss

    #### Getters

    def isReady(self) -> bool:
        return self.vehicle.armed and \
                self.vehicle.mode.name == "GUIDED" and \
                self.camera.running() and \
                self.vehicle.location.global_relative_frame.alt > 0.5 # Indicates we are actually flying

    def isAltitudeOk(self) -> bool:
        # TODO: This does not account for altitude at current position, only from home
        return self.vehicle.location.global_relative_frame.alt >= ALTITUDE - ALTITUDE_FUZZINESS

    def isConnected(self) -> bool:
        return self.vehicle.last_heartbeat < HEARTBEAT_TIMEOUT

    def armable(self) -> bool:
        return not self.vehicle.armed and \
                self.vehicle.is_armable and \
                self.vehicle.mode.name == "GUIDED" and \
                self.camera.running()

    #### State machine

    def run(self) -> None:
        while not self.state is ExecutionState.Stop:

            if self.state is ExecutionState.Init:
                # Do nothing during setup.
                time.sleep(1)
                pass
            elif self.state is ExecutionState.AwaitingArm:
                if self.armable():
                    time.sleep(5) # safety delay

                    if self.state != ExecutionState.Stop:
                        self.state = ExecutionState.Takeoff

                else:
                    time.sleep(1)

            elif self.state is ExecutionState.Takeoff:
                print('takeoff mode')

                # Takeoff and wait until we hit altitude

                # Confirm vehicle armed before attempting to take off
                while not self.vehicle.armed and self.state is ExecutionState.Takeoff:
                    self.vehicle.armed = True

                    print('Waiting for arming...')
                    time.sleep(1)

                # If state changes happens during the above inner loop
                if self.state != ExecutionState.Takeoff: continue

                print('Take off to ' + str(ALTITUDE) + 'm')
                self.vehicle.simple_takeoff(ALTITUDE)

                # Wait until the vehicle reaches altitude
                self.state = ExecutionState.AwaitingReady

            elif self.state is ExecutionState.AwaitingReady:
                if self.isReady() and self.isConnected() and self.isAltitudeOk():
                    # Prepare for running by resetting rules
                    for rule in self.rules:
                        rule.reset()

                    print('entered running state')

                    self.state = ExecutionState.Running

                # Shouldn't really happen, but here just in case!
                elif self.vehicle.mode.name != 'GUIDED':
                    self.state = ExecutionState.PilotOnly

                time.sleep(0.1)

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
                        self.activeRule = rule.name()
                        break

                # Apply local translation and yaw differential
                position, yaw = state
                setPositionTarget(self.vehicle, position, yaw)

                time.sleep(0.01)

            elif self.state is ExecutionState.ConnectionLoss:
                # until reconnected, nothing we can do.
                time.sleep(1)
                pass

            elif self.state is ExecutionState.PilotOnly:
                # Pilot is in control. Do nothing until we have disarmed again.
                time.sleep(1)
                pass

        # At this point, we are no longer running. Attempt to land if in-flight, else we
        # leave the platform in a dangerous state.

        if self.isReady() and self.isConnected() and self.isAltitudeOk():
            # Land now!
            self.vehicle.mode = VehicleMode('RTL')
            self.vehicle.wait_for_alt(0)

        if self.vehicle.armed:
            self.vehicle.disarm()

    def stop(self) -> None:
        self.state = ExecutionState.Stop

        # Cleanup
        self.vehicle.close()
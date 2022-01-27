from dronekit import connect
from enum import Enum
from constants import MIN_ALTITUDE, HEARTBEAT_TIMEOUT

class ExecutionState(Enum):
    Init          = 0
    AwaitingReady = 1
    Running       = 2
    Stop          = 3

class Core:

    vehicle = None
    state = ExecutionState.Init
    rules = []

    def __init__(self, vehicleUri):
        # Setup vehicle etc
        print("Connecting to vehicle on: %s" % (vehicleUri,))

        self.vehicle = connect(vehicleUri, wait_ready=True)
        self.vehicle.add_attribute_listener('mode', self.modeCallback)
        self.vehicle.add_attribute_listener('armed', self.armedCallback)
        self.vehicle.add_attribute_listener('last_heartbeat', self.lastHeartbeatCallback)

        # Setup rules

        # Enter ready state
        self.state = ExecutionState.AwaitingReady

    #### Callbacks

    def modeCallback(self, _):
        print("Vehicle mode %s" % (self.vehicle.mode,))

        if not self.isReady() and self.state != ExecutionState.Init:
            self.state = ExecutionState.AwaitingReady

    def armedCallback(self, _):
        print("Vehicle armed %d" % (self.vehicle.armed,))

        if not self.isReady() and self.state != ExecutionState.Init:
            self.state = ExecutionState.AwaitingReady

    def lastHeartbeatCallback(self, _):
        if not self.isConnected() and self.state != ExecutionState.Init:
            self.state = ExecutionState.AwaitingReady

    #### Getters

    def isReady(self):
        return self.vehicle.armed and \
                self.vehicle.mode.name == 'GUIDED' and \
                self.vehicle.location.global_relative_frame.alt > MIN_ALTITUDE

    def isConnected(self):
        return self.vehicle.last_heartbeat < HEARTBEAT_TIMEOUT

    #### State machine

    def run(self):
        while not self.state == ExecutionState.Stop:
            # Get camera data?

            if self.state is ExecutionState.Init:
                # Do nothing during setup.
                pass
            elif self.state is ExecutionState.AwaitingReady:

                if self.isReady() and self.isConnected():
                    self.state = ExecutionState.Running

            elif self.state is ExecutionState.Running:
                # Main implementation body
                pass

    def stop(self):
        self.state = ExecutionState.Stop

        # Cleanup
        self.vehicle.close()
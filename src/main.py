from dronekit import connect
from core import Core

def main(vehicleUri):
    print("Connecting to vehicle on: %s" % (vehicleUri,))

    vehicle = connect(vehicleUri, wait_ready=True)

    # Setup core
    core = Core(vehicle, None)
    core.run()

if __name__ == '__main__':
    main('')
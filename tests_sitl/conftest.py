import pytest
import time
import threading
import json

from typing import Tuple

from dronekit import connect
from dronekit import Vehicle
from dronekit_sitl import SITL

import os
import sys
sys.path.insert(0, './src')

from core import Core, ExecutionState
from camera.mock import MockCamera
from .uiconnection import UIConnection

ACTIVE_THREADS = []

@pytest.fixture
def environment():
    [core, vehicle, camera, sitl, ui] = prepareForTest()
    yield (vehicle, camera, core)
    shutdownAfterTest(sitl, core, camera, ui)

def core_thread(core):
    print('running core thread...')
    core.run()
    print('stopped core thread')

def ui_thread(ui: UIConnection, core: Core, vehicle: Vehicle, camera: MockCamera):
    print('running ui thread...')

    # On startup, send reset message
    resetMessage = { "type": "reset" }
    ui.send(json.dumps(resetMessage))

    while ui.active():
        # generate json blob of data to send
        vehicleGlobalFrame = vehicle.location.global_relative_frame
        vehicleLocalFrame = vehicle.location.local_frame

        if vehicleGlobalFrame.lat == 0.0 and vehicleGlobalFrame.lon == 0.0:
            time.sleep(0.1)
            continue

        message = {
            "type": "update",
            "vehicle": {
                "heading": vehicle.heading,
                "coordinates": {
                    "latitude": vehicleGlobalFrame.lat,
                    "longitude": vehicleGlobalFrame.lon,
                },
                "altitude": "{:.2f}".format(vehicleGlobalFrame.alt)
            },
            "core": {
                "state": core.state,
                "rule": core.activeRule
            }
        }

        detection = camera.closestDetection()
        if detection != None:
            message["person"] = {
                "global": camera.mockedPosition,
                "local": {
                    "x": detection.x,
                    "z": detection.z
                }
            }

        ui.send(message)

        time.sleep(0.1)

    # On shutdown, send reset message
    resetMessage = { "type": "reset" }
    ui.send(json.dumps(resetMessage))

    print('stopped ui thread')

def prepareForTest(timeout = True, verbose=False) -> Tuple[Core, Vehicle, MockCamera, SITL, UIConnection]:
    '''
    Prepares the SITL environment for a test.

    Should be called from a fixture
    '''

    print('start fixture')

    HOME = '-35.363261,149.165230,584,353'

    sitl = SITL(path=os.path.abspath('./.dronekit/arducopter'), defaults_filepath=os.path.abspath('./.dronekit/copter-hexa.parm'))
    sitl_args = ['--model', 'hexa']
    sitl.launch(sitl_args, await_ready=True, restart=False, verbose=verbose)

    connection_string = sitl.connection_string()

    print('connecting to ' + connection_string)

    vehicle = connect(connection_string, wait_ready=True, rate=10)
    camera = MockCamera(vehicle)

    core = Core(vehicle, camera)
    thread = threading.Thread(target=core_thread, args=(core,))
    thread.start()

    ACTIVE_THREADS.append(thread)

    ui = UIConnection()
    uithread = threading.Thread(target=ui_thread, args=(ui, core, vehicle, camera))
    uithread.start()

    ACTIVE_THREADS.append(uithread)

    print('init done')

    # Wait until the virtual drone hits the home position
    start = time.time()
    while True:
        # -35.363261 149.1652299
        location = vehicle.location.global_relative_frame
        print(location.lat, location.lon)

        if location.lat == -35.363261 and location.lon == 149.1652299:
            break

        if timeout and time.time() - start > 10:
            core.stop()
            raise ValueError('timeout on gps initial position exceeded')

        time.sleep(1)

    # Setup initial state to get the drone "flying"

    vehicle.mode = 'GUIDED'
    core.state = ExecutionState.Takeoff

    print('waiting for vehicle start')

    start = time.time()
    while True:
        if core.state == ExecutionState.Running:
            print('started')
            break

        if timeout and time.time() - start > 60:
            core.stop()
            raise ValueError('timeout on takeoff exceeded')

        time.sleep(1)

    return [core, vehicle, camera, sitl, ui]

def shutdownAfterTest(sitl, core: Core, camera: MockCamera, ui: UIConnection):
    '''
    Clears SITL environment after a test
    '''

    print('shutdown called')

    camera.stop()
    core.stop()
    ui.stop()

    if sitl != None:
        sitl.stop()
        print('stopped sitl')

    for thread in ACTIVE_THREADS:
        thread.join()
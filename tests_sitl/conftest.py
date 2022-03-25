import pytest
import time
import threading

from typing import Tuple

from dronekit import connect
from dronekit import Vehicle
from dronekit_sitl import SITL

import os
import sys
sys.path.insert(0, './src')

from core import Core, ExecutionState
from camera.mock import MockCamera

ACTIVE_THREADS = []

@pytest.fixture
def environment():
    [core, vehicle, camera, sitl] = prepareForTest()
    yield [vehicle, camera, core]
    shutdownAfterTest(sitl, core)

def core_thread(core):
    print('running core thread...')
    core.run()
    print('stopped core thread')

def prepareForTest(timeout = True) -> Tuple[Core, Vehicle, MockCamera, SITL]:
    '''
    Prepares the SITL environment for a test.

    Should be called from a fixture
    '''

    print('start fixture')

    HOME = '-35.363261,149.165230,584,353'

    sitl = SITL(path=os.path.abspath('./.dronekit/arducopter'), defaults_filepath=os.path.abspath('./.dronekit/copter-hexa.parm'))
    sitl_args = ['--model', 'hexa']
    sitl.launch(sitl_args, await_ready=True, restart=False)

    connection_string = sitl.connection_string()

    print('connecting to ' + connection_string)

    vehicle = connect(connection_string, wait_ready=True)
    camera = MockCamera()

    core = Core(vehicle, camera)
    thread = threading.Thread(target=core_thread, args=(core,))
    thread.start()

    ACTIVE_THREADS.append(thread)

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

    return [core, vehicle, camera, sitl]

def shutdownAfterTest(sitl, core):
    '''
    Clears SITL environment after a test
    '''

    print('shutdown called')

    core.stop()

    if sitl != None:
        sitl.stop()
        print('stopped sitl')

    for thread in ACTIVE_THREADS:
        thread.join()
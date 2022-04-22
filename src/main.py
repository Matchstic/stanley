import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

from dronekit import connect, Vehicle
from core import Core
from camera.yolocam import YoloCamera

import argparse
import os
import time
import threading
import signal
import cv2
import platform

if platform.machine() == 'aarch64':  # Jetson
    os.environ['OPENBLAS_CORETYPE'] = "ARMV8"

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

EXIT: bool         = False
core: Core         = None
camera: YoloCamera = None
vehicle: Vehicle   = None
videoWriter        = None

def core_thread(core):
    global EXIT

    if EXIT:
        return

    print('Running core')
    core.run()
    print('Stopped core')

def camera_callback(detections, cvFrame):
    global videoWriter
    videoWriter.write(cvFrame)

def stop():
    global EXIT, core, camera, vehicle

    EXIT = True

    if core:
        core.stop()

    if camera:
        camera.stop()

    print('DEBUG :: Stop finished')

def signal_handler(sig, frame):
    stop()

def main(args):
    global EXIT, core, camera, vehicle, videoWriter

    thread = None

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print('Searching for killswitch at: ' + args.killswitch_path)

    if os.path.exists(args.killswitch_path):
        print("Killswitch engaged, preventing run")
        while not EXIT:
            time.sleep(1)
    else:
        if args.video:
            print('Saving videos to: ' + args.video_path)

            if not os.path.exists(args.video_path):
                print('Video path ' + args.video_path + ' does not exist.')
                sys.exit(1)

            fileCount = len(os.listdir(args.video_path))
            videoWriter = cv2.VideoWriter(os.path.join(args.video_path, str(fileCount) + '.mkv'), cv2.VideoWriter_fourcc('M','J','P','G'), 30, YoloCamera.previewSize())

        print("Connecting to vehicle on: %s" % (args.uri,))
        vehicle = connect(args.uri, wait_ready=True)

        if not EXIT:
            camera = YoloCamera(camera_callback if args.video else None)
            camera.start()

            # Setup core thread
            core = Core(vehicle, camera)
            thread = threading.Thread(target=core_thread, args=(core,))
            thread.start()

            while not EXIT:
                print('DEBUG :: core state is: ' + core.state)
                time.sleep(1)

    # Signal handler will set the value of EXIT

    if thread:
        thread.join(5)

    if videoWriter:
        videoWriter.release()

    print('Thank you for flying Matchstic Air. We wish you a pleasant onward journey.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--uri', type=str, required=True, help="URI to connect with for MAVLink data. e.g., udp:127.0.0.1:14550")
    parser.add_argument('--video', required=False, default=False, help="Specify to save video of detections", action='store_true')
    parser.add_argument('--video_path', type=str, required=False, default=os.path.join(PARENT_DIRECTORY, 'videos'), help="Path to save video into")
    parser.add_argument('--killswitch_path', type=str, required=False, default=os.path.join(PARENT_DIRECTORY, 'killswitch'), help="Path to a file that if exists, this program will do nothing when ran")

    args = parser.parse_args()

    main(args)
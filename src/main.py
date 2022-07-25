import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import platform
import os
if platform.machine() == 'aarch64':  # Jetson
    os.environ['OPENBLAS_CORETYPE'] = "ARMV8"

from dronekit import connect, Vehicle
from core import Core
from camera.yolocam import YoloCamera

import argparse
import time
import threading
import signal
import cv2
import platform
import logging

PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

EXIT: bool         = False
core: Core         = None
camera: YoloCamera = None
vehicle: Vehicle   = None
videoWriter        = None

# See: https://stackoverflow.com/a/66209331
class LoggerWriter:
    def __init__(self, logfct):
        self.logfct = logfct
        self.buf = []

    def write(self, msg):
        if msg.endswith('\n'):
            self.buf.append(msg.removesuffix('\n'))
            self.logfct(''.join(self.buf))
            self.buf = []
        else:
            self.buf.append(msg)

    def flush(self):
        pass

def core_thread(core):
    global EXIT

    if EXIT:
        return

    logging.debug('Running core')
    core.run()
    logging.debug('Stopped core')

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

def signal_handler(sig, frame):
    stop()

def main(args):
    global EXIT, core, camera, vehicle, videoWriter

    thread = None

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Setup the log file
    logpath = args.log_path
    if not os.path.exists(logpath):
        logpath = os.path.join(PARENT_DIRECTORY, 'logs')

        print('WARNING Log path not found, redirecting to: ' + os.path.join(PARENT_DIRECTORY, 'logs'))

        # In the event the user has not got a relative `logs` folder
        if not os.path.exists(logpath):
            os.mkdir(logpath)

    fileCount = len(os.listdir(logpath))
    logFile = os.path.join(logpath, str(fileCount) + '.log')

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(levelname)-8s %(message)s",
        handlers=[
            logging.FileHandler(logFile),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger()

    # messing around with stdout for logging to file
    # this is nasty but whatever
    sys.stdout = LoggerWriter(logger.info)
    sys.stderr = LoggerWriter(logger.error)

    videoEnabled = args.video
    if args.video:
        logging.info('Saving videos to: ' + args.video_path)

        if not os.path.exists(args.video_path):
            logging.warning('Video path ' + args.video_path + ' does not exist, not recording video.')
            videoEnabled = False
        else:
            fileCount = len(os.listdir(args.video_path))
            videoWriter = cv2.VideoWriter(os.path.join(args.video_path, str(fileCount) + '.mkv'), cv2.VideoWriter_fourcc('M','J','P','G'), 30, YoloCamera.previewSize())

    if not EXIT:
        camera = YoloCamera(camera_callback if videoEnabled else None)
        camera.start()

        logging.info('Searching for killswitch at: ' + args.killswitch_path)
        if os.path.exists(args.killswitch_path):
            logging.warning("Killswitch engaged, preventing core run")
            while not EXIT:
                time.sleep(1)
        else:
            logging.info("Starting core")
            logging.info("Connecting to vehicle on: %s" % (args.uri,))
            vehicle = connect(args.uri, wait_ready=['gps_0', 'armed', 'mode', 'attitude'], rate=20)

            # Setup core thread
            core = Core(vehicle, camera)
            thread = threading.Thread(target=core_thread, args=(core,))
            thread.start()

            while not EXIT:
                logging.debug('core state is: ' + core.state + ', ' + core.activeRule)
                time.sleep(1)

    # Signal handler will set the value of EXIT

    if thread:
        thread.join(5)

    if videoWriter:
        videoWriter.release()

    logging.info('Thank you for flying Matchstic Air. We wish you a pleasant onward journey.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--uri', type=str, required=True, help="URI to connect with for MAVLink data. e.g., udp:127.0.0.1:14550")
    parser.add_argument('--video', required=False, default=False, help="Specify to save video of detections", action='store_true')
    parser.add_argument('--log_path', type=str, required=False, default=os.path.join(PARENT_DIRECTORY, 'logs'), help="Path to save log output into")
    parser.add_argument('--video_path', type=str, required=False, default=os.path.join(PARENT_DIRECTORY, 'videos'), help="Path to save video into")
    parser.add_argument('--killswitch_path', type=str, required=False, default=os.path.join(PARENT_DIRECTORY, 'killswitch'), help="Path to a file that if exists, this program will do nothing when ran")

    args = parser.parse_args()

    main(args)
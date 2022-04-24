import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

sys.path.insert(0, './src')

from src.camera.yolocam import YoloCamera
import cv2

EXIT = False
HAS_FRAME = False
FRAME = None

camera = None

def callback(detections, frame):
    global EXIT
    global FRAME
    global HAS_FRAME

    print(str(camera.closestDetection().z) + ', confidence: ' + \
          str(camera.closestDetection().confidence) if len(detections) > 0 else 'no detection')
    FRAME = frame
    HAS_FRAME = True

camera = YoloCamera(callback)
camera.start()

try:
    while EXIT == False:
        if HAS_FRAME:
            cv2.imshow("rgb", FRAME)
            if cv2.waitKey(1) == ord('q'):
                EXIT = True
except KeyboardInterrupt:
    EXIT = True

camera.stop()
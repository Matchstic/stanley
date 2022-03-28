import sys
sys.path.insert(0, './src/camera')

from src.camera.yolocam import YoloCamera
import cv2

EXIT = False
HAS_FRAME = False
FRAME = None

def callback(detections, frame):
    global EXIT
    global FRAME
    global HAS_FRAME

    print(detections[0].z if len(detections) > 0 else 'no detection')
    FRAME = frame
    HAS_FRAME = True

camera = YoloCamera(None)
camera.start()

while EXIT == False:
    if HAS_FRAME:
        cv2.imshow("rgb", FRAME)
        if cv2.waitKey(1) == ord('q'):
            EXIT = True

camera.stop()
from .metadata import Metadata
from .detection import Detection

import numpy
import cv2

'''
Used to generate camera previews for debugging purposes
'''
class PreviewGenerator:
    def generate(self, frame: numpy.ndarray, detections: list[Detection], metadata: Metadata):
        height = metadata.frameHeight
        width = metadata.frameWidth

        annotatedFrame = frame.copy()

        textColor = (0, 0, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontSize = 0.4
        xStart = 8
        yHeight = 20

        # Render bounding boxes per detection
        for detection in detections:
            # Denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            
            cv2.rectangle(annotatedFrame, (x1, y1), (x2, y2), textColor, font)

        # FPS
        cv2.putText(annotatedFrame, "NN (fps): {:.2f}".format(metadata.fps), (xStart, yHeight*4), font, fontSize, textColor)

        # Distance values
        if len(detections) == 0:
            cv2.putText(annotatedFrame, "X (m): 0", (xStart, yHeight), font, fontSize, textColor)
            cv2.putText(annotatedFrame, "Y (m): 0", (xStart, yHeight*2), font, fontSize, textColor)
            cv2.putText(annotatedFrame, "Z (m): 0", (xStart, yHeight*3), font, fontSize, textColor)
        else:
            closest = None

            for detection in detections:
                if closest == None: closest = detection
                elif closest.z > detection.z: closest = detection

            cv2.putText(annotatedFrame, f"X (m): {closest.x:.2f}", (xStart, yHeight), font, fontSize, textColor)
            cv2.putText(annotatedFrame, f"Y (m): {closest.y:.2f}", (xStart, yHeight*2), font, fontSize, textColor)
            cv2.putText(annotatedFrame, f"Z (m): {closest.z:.2f}", (xStart, yHeight*3), font, fontSize, textColor)

        return annotatedFrame

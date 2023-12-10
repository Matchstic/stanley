from ultralytics import YOLO
import math 
from pathlib import Path

from .model import BaseGestureModel
from .detection import GestureDetection

BLOB_PATH = str((Path(__file__).parent / Path('../../models/gestures.pt')).resolve().absolute())

class PyTorchGestureModel(BaseGestureModel):
    model = None
    names = None

    def __init__(self) -> None:
        self.model = YOLO(BLOB_PATH)
        self.names = self.model.names

    def inference(self, frame) -> [GestureDetection]:
        results = []
        inferenceResults = self.model(frame, stream=True)

        for r in inferenceResults:
            boxes = r.boxes

            for box in boxes:
                confidence = math.ceil((box.conf[0]*100))/100
                if confidence < 0.7: continue

                cls = int(box.cls[0])
                name = self.names[cls]

                results.append(GestureDetection(name, confidence))

        return results

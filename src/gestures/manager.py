import multiprocessing
from enum import Enum

from .model import BaseGestureModel
from .detection import GestureDetection

from .pytorch import PyTorchGestureModel
from .tensorRT import TensorRTGestureModel

class GestureProcess(multiprocessing.Process):
    model: BaseGestureModel

    def __init__(self, task_queue, results_queue, model):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.results_queue = results_queue

        if model is "pytorch":
            self.model = PyTorchGestureModel()
        elif model is "tensorrt":
            self.model = TensorRTGestureModel()
        else:
            raise Exception("A gesture model needs to be specified!")

    def run(self):
        while True:
            next_task = self.task_queue.get()
            if next_task is "exit":
                self.task_queue.task_done()
                break
            elif next_task is None:
                continue

            print("DEBUG :: Handling frame")
            frame = next_task
            results = self.model.inference(frame)

            self.task_queue.task_done()
            self.results_queue.put(results)
        return

class GestureManagerState(Enum):
    EXPECTING_NEW_FRAME = 1
    AWAITING_RESULTS = 2

class GestureManager:
    frames = multiprocessing.Queue()
    results = multiprocessing.Queue()
    process: GestureProcess

    model = ""
    currentDetections: [GestureDetection] = []
    
    frameState = GestureManagerState.EXPECTING_NEW_FRAME

    def __init__(self, model = "pytorch") -> None:
        self.model = model

    def start(self):
        self.process = GestureProcess(self.frames, self.results, self.model)
        self.process.start()

    def onNewFrame(self, frame) -> None:
        if self.frameState is GestureManagerState.EXPECTING_NEW_FRAME:

            self.frames.put_nowait(frame)
            self.frameState = GestureManagerState.AWAITING_RESULTS

        elif self.frameState is GestureManagerState.AWAITING_RESULTS:

            try:
                self.currentDetections = self.results.get_nowait()
                self.frameState = GestureManagerState.EXPECTING_NEW_FRAME
            except:
                pass
        
    def detections(self) -> [GestureDetection]:
        return self.currentDetections

    def shutdown(self):
        self.frames.put("exit")
        self.process.join()

        self.frames.close()
        self.results.close()
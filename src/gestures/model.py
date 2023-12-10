from .detection import GestureDetection

class BaseGestureModel:
    model = None
    names = None

    def __init__(self) -> None:
        pass

    def inference(self, frame) -> [GestureDetection]:
        return []
class BaseCamera:

    def __init__(self):
        pass

    def detections(self):
        return []

    def start(self):
        pass

    def stop(self):
        pass

    def closestDetection(self):
        closest = None

        for detection in self.detections():
            if closest == None: closest = detection
            elif closest.z > detection.z: closest = detection

        return closest
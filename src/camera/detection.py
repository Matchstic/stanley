'''
A detection represents the location of a person, relative to the center of
the camera's reference frame.
'''
class Detection():

    x = 0
    y = 0
    z = 0
    confidence = 0
    fps = 0

    def __init__(self, x, y, z, confidence, fps):
        # NOTE: incoming parameters are all mm. We want to expose in meters

        self.x = x / 1000.0
        self.y = y / 1000.0
        self.z = z / 1000.0
        self.confidence = confidence
        self.fps = fps
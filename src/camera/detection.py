'''
A detection represents the location of a person, relative to the center of
the camera's reference frame.
'''
class Detection():

    x = 0
    xmin = 0
    xmax = 0

    y = 0
    ymin = 0
    ymax = 0

    z = 0
    confidence = 0
    fps = 0

    def __init__(self, x, y, z, confidence, fps, xmin, xmax, ymin, ymax):
        # NOTE: incoming parameters are all m.

        self.x = x
        self.y = y
        self.z = z
        self.confidence = confidence
        self.fps = fps

        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        
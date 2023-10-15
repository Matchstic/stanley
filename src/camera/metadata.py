'''
Represents metadata about the capturing camera
'''
class Metadata():

    frameWidth = 0
    frameHeight = 0
    fps = 0

    def __init__(self, frameWidth, frameHeight, fps):
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.fps = fps
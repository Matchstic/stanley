class Detection():

    absoluteX = 0
    absoluteY = 0
    absoluteZ = 0

    def toCameraSpace(self, camera):
        ''' Converts detection to corresponding location in the
        camera's reference frame.
        '''
        return (0, 0, 0)
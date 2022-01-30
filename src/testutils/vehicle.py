class MockVehicle():
    '''A mock implementation of the DroneKit vehicle class'''

    _mode = 'GUIDED'
    _armed = False
    _listeners = {}

    def add_attribute_listener(self, parameter, fn):
        listenerList = self._listeners[parameter]
        if listenerList is None:
            listenerList = []

        listenerList.append(fn)

    def _applyCallback(self, parameter, value):
        listenerList = self._listeners[parameter]
        if listenerList:
            for l in listenerList:
                l(parameter, value)

    @property
    def armed(self):
        return self._armed

    @armed.setter
    def armed(self, value):
        self._armed = value
        self._applyCallback('armed', value)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self._applyCallback('mode', value)
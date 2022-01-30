import unittest
from utils import prepareForTest

class BaseTest(unittest.TestCase):

    vehicle = None
    camera = None

    def __init__(self, vehicle, camera):
        self.vehicle = vehicle
        self.camera = camera

    def setUp(self) -> None:
        prepareForTest()
        return super().setUp()

if __name__ == '__main__':
    unittest.main()
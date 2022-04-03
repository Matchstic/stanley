from .utils import headingDiff, gpsDistance, Environment
import time

def test_drone_does_not_rotate(environment: Environment):
    vehicle, _, _ = environment

    heading = vehicle.heading

    time.sleep(5)

    difference = headingDiff(heading, vehicle.heading)
    print(difference)

    assert abs(difference) < 3

def test_drone_does_not_drift(environment: Environment):
    vehicle, _, _ = environment

    location1 = vehicle.location.global_frame

    time.sleep(5)

    location2 = vehicle.location.global_frame

    difference = gpsDistance(location1.lat, location1.lon, location2.lat, location2.lon)
    assert abs(difference) < 1
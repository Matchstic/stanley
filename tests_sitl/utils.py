# Set of useful utilities when running an integration test

import math

from core import Core
from typing import Tuple
from camera.mock import MockCamera
from dronekit import Vehicle

RADIUS_OF_EARTH = 6378100.0  # in meters
Environment = Tuple[Vehicle, MockCamera, Core]

def headingDiff(h1, h2) -> int:
    '''
    The difference of two headings in degrees such that it is always in the range
    (-180, 180]. A negative number indicates [h2] is to the left of [h1].
    '''

    left = h1 - h2
    right = h2 - h1

    if left < 0: left += 360
    if right < 0: right += 360

    return -left if left < right else right

def gpsDistance(lat1, lon1, lat2, lon2):
    """Return distance between two points in meters,
    coordinates are in degrees
    thanks to http://www.movable-type.co.uk/scripts/latlong.html ."""
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = math.sin(0.5 * dLat)**2 + math.sin(0.5 * dLon)**2 * math.cos(lat1) * math.cos(lat2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return RADIUS_OF_EARTH * c
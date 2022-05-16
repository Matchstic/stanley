from time import time
from tests_sitl.conftest import prepareForTest, shutdownAfterTest
import time

[core, vehicle, camera, sitl, ui] = prepareForTest(timeout=False, verbose=False)

def uicallback(data):
    # Set person in mock camera
    if data["type"] == "control":
        latitude = data["latitude"]
        longitude = data["longitude"]

        camera.setGlobalCoordinate(latitude, longitude)

ui.setOnDataCallback(uicallback)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

shutdownAfterTest(sitl, core, camera, ui)
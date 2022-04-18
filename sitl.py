from time import time
from tests_sitl.utils import prepareForTest, shutdownAfterTest
import time

[core, vehicle, camera, sitl, ui] = prepareForTest(timeout=False)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

shutdownAfterTest(sitl, core, camera, ui)
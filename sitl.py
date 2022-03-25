from time import time
from tests_sitl.utils import prepareForTest, shutdownAfterTest
import time

[core, vehicle, camera, sitl] = prepareForTest(timeout=False)

stop = False
while not stop:
    try:


        time.sleep(1)
    except KeyboardInterrupt:
        shutdownAfterTest(sitl, core)
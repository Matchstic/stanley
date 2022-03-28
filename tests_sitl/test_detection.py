'''

Test cases:
- In "no detection" LOITER, and switch to GUIDED
- Lose detection and search
- Lose detection and re-establish it
- effectively LOITER when detection remains stationary
- distance is never closer than 2 meters

Will need:
- Conversion from GPX trace into camera-space detections (heading and position etc)
- GPX playback in real-time (making sure to interpolate position)
- A way to specify the current trace during test start-up (method on mock camera)

'''
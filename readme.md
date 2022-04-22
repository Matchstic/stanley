## Stanley

This is the source for my autonomous drone project, Stanley.

It makes use of the OAK-D Lite for detecting people with depth (TinyYOLO v4), and then uses a subsumption architecture to send control signals
via MAVLink to a drone to follow the closest person.

The full project is intended to run on an NVIDIA Jetson Nano, but should work on any platform that can talk via MAVLink, and can run `depthai`.

- INFO: This project is very much work-in-progress. Do not expect anything to work.
- **WARNING**: I take no responsibility if you run any of this code on your own drone. You do so at your own risk.

### Getting Started

https://docs.luxonis.com/en/latest/pages/tutorials/first_steps/

- `./setup.sh` for dependencies
- `python utils/camera.py` to debug Yolo detections and FPS
- `./integration.sh` to run SITL integration tests
- `python sitl.py` to run virtualised SITL mode with direct person control
- `cd visualiser && yarn serve` to run the SITL frontend
- `python main.py` to run the full system - see the help it logs with `-h`

### Testing (SITL)

A full SITL environment is used for testing, and I have built a visualisation tool in `vue` to serve as a frontend.

- TODO: `yarn serve` etc, WebSockets blah blah
- TODO: `.dronekit/arducopter` is built for macOS

I wrote some integration tests, but definitely don't have full coverage.

### License

Licensed under GPLv3.

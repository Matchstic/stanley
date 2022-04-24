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


### Jetson Nano

```
sudo apt install zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev
cd ~/Downloads
wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tar.xz
tar xvf Python-3.9.12.tar.xz
mkdir build-python-3.9
cd build-python-3.9
../Python-3.9.12/configure --enable-optimizations
make -j $(nproc)
make altinstall
python3.9 -m pip install wheel # needed to install pymavlink correctly
```

https://docs.luxonis.com/projects/api/en/v2.2.1.0/install/#ubuntu

```
python3.9 -m pip install dronekit dronekit-sitl pymavlink pytest depthai-sdk gpxpy websockets asyncio
```

Setup udev rules:

```
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

if using MAVProxy already on the system, make sure to start it with `--out 127.0.0.1:14550`. Then, can run `python3.9 src/main.py --uri 127.0.0.1:14550`

### License

Licensed under GPLv3.

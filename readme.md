## Stanley

This is the source for my autonomous drone project, Stanley.

It makes use of the OAK-D Lite for detecting people with depth (TinyYOLO v4), and then uses a subsumption architecture to send control signals
via MAVLink to a drone to follow the closest person.

The full project is intended to run on an NVIDIA Jetson Nano, but should work on any platform that can talk via MAVLink, and can run `depthai`.

- INFO: This project is very much work-in-progress. It should be functional, but be prepared to dive into the code to fix things.
- **WARNING**: I take no responsibility if you run any of this code on your own drone. You do so at your own risk.

### Getting Started

I went through the process here to setup my own drone: https://docs.luxonis.com/en/latest/pages/tutorials/first_steps/

- run `./setup.sh` to install dependencies
- `python utils/camera.py` is for debugging Yolo detections and FPS
- `./integration.sh` to run SITL integration tests
- `python sitl.py` to run virtualised SITL mode with direct person control
- `cd visualiser && yarn serve` to run the SITL frontend
- `python src/main.py` to run the full system - see the help it logs with `-h`

### Testing (SITL)

A full SITL environment is used for testing, and I have built a visualisation tool in `vue` to serve as a frontend.

To use this visualiser, you should open two terminal windows. In the first, run:

```bash
cd visualiser
yarn install
yarn serve
```

This will start the visualiser UI, which will be available on `localhost:8080`. This communicates via WebSockets to the SITL backend, which runs the `Core` class internally, as well as a mocked camera instance.

Then, in the other terminal window, run 

```bash
python sitl.py
```

This will then start the backend. If the frontend UI doesn't connect automatically, hit refresh in your browser. Data should eventually start coming through - there likely will be a delay before it starts.

Please note: the compiled version of ArduPilot 4.1 (`.dronekit/arducopter`) is for macOS. You will likely need to change `sitl.py` to use one for Windows or Linux as required.

### Testing (integration tests)

I wrote some integration tests for this project, but definitely don't have full coverage - I mainly used the visualiser to test changes to rules.

### Setup on companion computer

**Pre-requisites**: [MAVProxy](https://ardupilot.org/mavproxy/docs/getting_started/download_and_installation.html)

The base image for the Jetson Nano likely has Python 3.6 installed, but this code requires 3.9+. To install this new runtime, do the following:

```bash
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

Now, you can go through the steps to install DepthAI on the Nano. You should follow the steps specifically for the Jetson family here: https://docs.luxonis.com/projects/api/en/v2.2.1.0/install/#ubuntu

Next, install the Python dependencies:

```bash
python3.9 -m pip install dronekit dronekit-sitl pymavlink pytest depthai-sdk gpxpy websockets asyncio
```

Then, setup the `udev` rules needed for the OAK-D Lite to function properly:

```
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

At this point, all the dependencies are installed, and you can grab this repo with:

```bash
cd ~
git clone https://github.com/Matchstic/stanley.git
```

If you're using MAVProxy already on the system, make sure to start it with `--out 127.0.0.1:14550`. Then, you can run `python3.9 src/main.py --uri 127.0.0.1:14550`

**OPTIONAL**

You can setup a `systemd` service to load `main.py` on boot. To do this, update the various parameters inside `<>` in `stanley.service`. Then, you can run:

```bash
sudo cp stanley.service /lib/systemd/system/
sudo systemctl enable stanley.service
```

### License

Licensed under GPLv3.

### Create Virtual Serial Ports
#### Install socat
```
sudo apt update
sudo apt install socat
```

#### Create virtual serial ports 
Use the following command to create a pair of linked virtual serial ports with fixed device names:
```
socat -d -d \
pty,raw,echo=0,link=/tmp/ttyV0 \
pty,raw,echo=0,link=/tmp/ttyV1
```

### Install grblHAL Simulator
```
git clone --recurse-submodules https://github.com/grblHAL/Simulator
cd Simulator
mkdir build && cd build
cmake ..
make
```

### Start grblHAL_sim
This is a CNC simulator able to receive gcode from bCNC
```
socat /tmp/ttyV1,raw,echo=0 \
EXEC:'./Simulator/build/grblHAL_sim -n',pty,raw,echo=0
```

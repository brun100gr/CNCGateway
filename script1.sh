#!/bin/bash

# ===============================
# Setup automatico bCNC + seriale
# ===============================

VTTY0="/tmp/ttyV0"
VTTY1="/tmp/ttyV1"
VTTY2="/tmp/ttyV2"
VTTY3="/tmp/ttyV3"

echo "Create virtual serial ports and start bCNC"

# Kill socat if already running
pkill socat

# Definizione porte virtuali

# Lancia socat solo se le porte non esistono già
SOCAT_PIDS=""

# Coppia 1: VTTY0 <-> VTTY1
if [ ! -e "$VTTY0" ] || [ ! -e "$VTTY1" ]; then
    echo "Creating virtual serial ports $VTTY0 <-> $VTTY1 ..."
    socat -d -d \
        pty,raw,echo=0,link=$VTTY0,mode=666 \
        pty,raw,echo=0,link=$VTTY1,mode=666 &
    SOCAT_PIDS="$SOCAT_PIDS $!"
    sleep 1
else
    echo "Virtual serial ports $VTTY0 and $VTTY1 already exist."
fi

# Coppia 2: VTTY2 <-> VTTY3
if [ ! -e "$VTTY2" ] || [ ! -e "$VTTY3" ]; then
    echo "Creating virtual serial ports $VTTY2 <-> $VTTY3 ..."
    socat -d -d \
        pty,raw,echo=0,link=$VTTY2,mode=666 \
        pty,raw,echo=0,link=$VTTY3,mode=666 &
    SOCAT_PIDS="$SOCAT_PIDS $!"
    sleep 1
else
    echo "Virtual serial ports $VTTY2 e $VTTY3 already exist."
fi

echo "Socat PIDs: $SOCAT_PIDS"

REAL_PTY0=$(readlink -f $VTTY0)
echo "---> Virtual serial $VTTY0 points to $REAL_PTY0"

REAL_PTY1=$(readlink -f $VTTY1)
echo "---> Virtual serial $VTTY1 points to $REAL_PTY1"

REAL_PTY2=$(readlink -f $VTTY2)
echo "---> Virtual serial $VTTY2 points to $REAL_PTY2"

REAL_PTY3=$(readlink -f $VTTY3)
echo "---> Virtual serial $VTTY3 points to $REAL_PTY3"

chmod 666 $REAL_PTY0

# Verifica che DISPLAY sia settato
if [ -z "$DISPLAY" ]; then
    echo "ERROR: DISPLAY is not set. Are you running in a graphical session?"
    exit 1
fi
echo "Using DISPLAY=$DISPLAY"

# Abilita accesso X per container locali
xhost +local:docker 2>/dev/null || xhost +local:

# Avvia Docker con X forwarding corretto
docker run -it --rm \
    --privileged \
    -e DISPLAY="$DISPLAY" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $HOME/.Xauthority:/root/.Xauthority:ro \
    -v $PWD/bCNC:/home/cncuser/.bCNC \
    -v $PWD/projects:/home/cncuser/projects \
    -v /dev/pts:/dev/pts \
    bcnc bash -c "echo 'Use this serial port inside bCNC: $REAL_PTY0' && exec python3 -m bCNC"

# Ferma socat se era stato lanciato dallo script
if [ -n "$SOCAT_PIDS" ]; then
    echo "Stopping socat..."
    for pid in $SOCAT_PIDS; do
        kill $pid 2>/dev/null
    done
fi

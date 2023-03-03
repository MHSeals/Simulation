#!/usr/bin/env bash

docker run \
    --interactive \
    --tty \
    --rm \
    --shm-size=16G \
    --device=/dev/dxg \
    --gpus=all
    --env DISPLAY=$DISPLAY \
    --env WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
    --env XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
    --env PULSE_SERVER=$PULSE_SERVER \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume="/mnt/wslg:/mnt/wslg" \
    --volume="/usr/lib/wsl:/usr/lib/wsl" \
    glxinfo | grep "OpenGL"

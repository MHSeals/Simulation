#!/usr/bin/env bash

# this is potentially dangerous
# a more appropriate approach is used in run.sh
xhost +

docker run \
    --interactive \
    --tty \
    --rm \
    --privileged \
    --volume=/tmp/.X11-unix:/tmp/.X11-unix \
    --device=/dev/dri:/dev/dri \
    --env="DISPLAY=$DISPLAY" \
    roboboat \
    glxinfo | grep "OpenGL"

xhost -
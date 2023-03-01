#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MODEL_DIR=$( cd -- "$( dirname -- "${SCRIPT_DIR}" )" &> /dev/null && pwd )/Models
PYTHON_DIR=$( cd -- "$( dirname -- "${SCRIPT_DIR}" )" &> /dev/null && pwd )/Python

IMAGE_NAME=roboboat
IMAGE_TAG=simulator-nvidia

xhost +

docker run \
    --tty \
    --interactive \
    --rm \
    --device "/dev/dri:/dev/dri" \
    --privileged \
    --runtime nvidia \
    --gpus all \
    --shm-size 16G \
    --network host \
    --env "DISPLAY=$DISPLAY" \
    --volume "/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume "${PYTHON_DIR}:/root/src/roboboat-code" \
    --volume "${MODEL_DIR}:/root/src/roboboat-models" \
    ${IMAGE_NAME}:${IMAGE_TAG} \
    bash
    # cd /root/src/px4-autopilot && make px4_sitl gazebo-classic_boat

xhost -
#!/usr/bin/env bash

docker pull mhseals/roboboat-simulation:wsl2-nvidia

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MODEL_DIR=$( cd -- "$( dirname -- "${SCRIPT_DIR}" )" &> /dev/null && pwd )/Models
PYTHON_DIR=$( cd -- "$( dirname -- "${SCRIPT_DIR}" )" &> /dev/null && pwd )/Python

CONTAINER_NAME=roboboat-simulator
IMAGE_NAME=mhseals/roboboat-simulation
IMAGE_TAG=wsl2-nvidia

# get docker container ID if exists
CONTAINER_ID=`docker ps -aqf "name=^/${CONTAINER_NAME}$"`

if [ -z "${CONTAINER_ID}" ]; then

    docker run \
        --detach \
        --tty \
        --shm-size=16G \
        --device=/dev/dxg \
        --gpus=all \
        --name ${CONTAINER_NAME} \
        --publish 18530:18530/udp \
        --publish 18570:18570/udp \
        --publish 18550:18550/udp \
        --publish 14550:14550/udp \
        --publish 14570:14570/udp \
        --publish 14530:14530/udp \
        --publish 5600:5600/udp \
        --env DISPLAY=$DISPLAY \
        --env WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
        --env XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
        --env PULSE_SERVER=$PULSE_SERVER \
        --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
        --volume="/mnt/wslg:/mnt/wslg" \
        --volume="/usr/lib/wsl:/usr/lib/wsl" \
        --volume "${PYTHON_DIR}:/root/src/roboboat-code" \
        --volume "${MODEL_DIR}:/root/src/roboboat-models" \
        ${IMAGE_NAME}:${IMAGE_TAG}

else
    xhost +local:`docker inspect --format='{{ .Config.Hostname }}' ${CONTAINER_ID}`

    if [ -z `docker ps -qf "name=^/${CONTAINER_NAME}$"` ]; then
        echo "${CONTAINER_NAME} container not running. Starting container..."
        docker start ${CONTAINER_ID}
    else
        echo "Attaching to running ${CONTAINER_NAME} container..."
    fi
    docker exec -it ${CONTAINER_ID} bash

    xhost -local:`docker inspect --format='{{ .Config.Hostname }}' ${CONTAINER_ID}`
fi
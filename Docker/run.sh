#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MODEL_DIR=$( cd -- "$( dirname -- "${SCRIPT_DIR}" )" &> /dev/null && pwd )/Models
PYTHON_DIR=$( cd -- "$( dirname -- "${SCRIPT_DIR}" )" &> /dev/null && pwd )/Python

CONTAINER_NAME=roboboat-simulator
IMAGE_NAME=mhseals/roboboat-simulation
IMAGE_TAG=linux-intel

# get docker container ID if exists
CONTAINER_ID=`docker ps -aqf "name=^/${CONTAINER_NAME}$"`

if [ -z "${CONTAINER_ID}" ]; then

    docker run \
        --tty \
        --detach \
        --name ${CONTAINER_NAME} \
        --device "/dev/dri:/dev/dri" \
        --privileged \
        --shm-size 16G \
        --network host \
        --env "DISPLAY=$DISPLAY" \
        --volume "/tmp/.X11-unix:/tmp/.X11-unix" \
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

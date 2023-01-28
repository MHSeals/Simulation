#!/usr/bin/env bash

# see http://wiki.ros.org/docker/Tutorials/Hardware%20Acceleration#Intel

# get the script parent directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# define the 'src' folder path
SRC_DIR=${SCRIPT_DIR}/src

# define Docker image name
# we don't need image tag here because it defaults to latest
IMAGE_NAME=roboboat

# give your container a name
CONTAINER_NAME=roboboat-container

# check docker if container exists
CONTAINER_ID=`docker ps -aqf "name=^/${CONTAINER_NAME}$"`

# if container with name not found
if [ -z "${CONTAINER_ID}" ]; then

    # this will just create a container
    # detach from it, and you can access it later
    # THIS CONTAINER WILL PERSIST! but it will be automatically
    # stopped when your computer reboots
    docker run \
        --interactive \
        --detach \
        --privileged \
        --network host \
        --device=/dev/dri:/dev/dri \
        --name ${CONTAINER_NAME} \
        --env "DISPLAY=$DISPLAY" \
        --volume "/tmp/.X11-unix:/tmp/.X11-unix" \
        --volume "${SRC_DIR}:/root/src" \
        $IMAGE_NAME

else

    # allow X Server access
    xhost +local:`docker inspect --format='{{ .Config.Hostname }}' ${CONTAINER_ID}`

    # Check if the container is already running and start if necessary.
    if [ -z `docker ps -qf "name=^/${CONTAINER_NAME}$"` ]; then
        echo "${CONTAINER_NAME} container not running. Starting container..."
        docker start ${CONTAINER_ID}
    else
        echo "Attaching to running ${CONTAINER_NAME} container..."
    fi
    docker exec -it ${CONTAINER_ID} bash

    # remove previous access
    xhost -local:`docker inspect --format='{{ .Config.Hostname }}' ${CONTAINER_ID}`

fi

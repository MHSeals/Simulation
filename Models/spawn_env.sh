#!/usr/bin/env bash

# WARN='\033[1;33m'
# CLEAR='\033[0m'

SRC_DIR=/root/src/px4-autopilot
BUILD_DIR=${SRC_DIR}/build/px4_sitl_default

export GAZEBO_PLUGIN_PATH=${BUILD_DIR}/build_gazebo-classic
export GAZEBO_MODEL_PATH=${SRC_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models
export LD_LIBRARY_PATH=${BUILD_DIR}/build_gazebo-classic
export PX4_SIM_MODEL=gazebo-classic_boat

WORLD_PATH="/root/src/roboboat-models/benderson_park.world"
BOAT_PATH="/root/src/roboboat-models/Boat/boat.sdf"
# BOAT_PATH=$(echo ${GAZEBO_MODEL_PATH}/boat/boat.sdf | tr -d '\r')
RED_BUOY_PATH="/root/src/roboboat-models/Buoy/red_buoy.sdf"
GREEN_BUOY_PATH="/root/src/roboboat-models/Buoy/green_buoy.sdf"

set -e

rootfs="/root/src/px4-autopilot/build/sitl_default/rootfs" # this is the working directory
mkdir -p "$rootfs"

# reset sim PID
SIM_PID=0

# kill previous gazebo if exists
pkill -x gazebo || true
pkill -x gzserver || true

# start gzserver with our world
# gzserver empty.world &
gzserver ${WORLD_PATH} &

# spawn our boat
while ! gz model --verbose --spawn-file="${BOAT_PATH}" --model-name=bote -x 0 -y 0 -z 1 -Y 3.14; 
do
    echo "gzserver not ready yet, trying again!"
    sleep 1
done

# spawn our obstacles
# while ! gz model --verbose --spawn-file="${RED_BUOY_PATH}" --model-name=rbuoy1 -x -15 -y -3 -z 1; 
# do
#     echo "gzserver not ready yet, trying again!"
#     sleep 1
# done

# while ! gz model --verbose --spawn-file="${GREEN_BUOY_PATH}" --model-name=gbuoy1 -x -15 -y 3 -z 1; 
# do
#     echo "gzserver not ready yet, trying again!"
#     sleep 1
# done

# save gzserver PID to kill later
SIM_PID=$!

# start gzclient GUI, not following
sleep 3
nice -n 20 gzclient --verbose --gui-client-plugin libgazebo_user_camera_plugin.so &

# save gzclient PID to kill later
GUI_PID=$!

pushd "$rootfs" >/dev/null

# no longer kill on error
set +e

# starts SITL
eval /root/src/px4-autopilot/build/px4_sitl_default/bin/px4 -d /root/src/px4-autopilot/build/px4_sitl_default/etc

# killing everything
echo -n "Killing gzserver in background (pid ${SIM_PID})... " && kill -9 $SIM_PID && echo "Done."
echo -n "Killing gzclient in background (pid ${GUI_PID})... " && kill -9 $GUI_PID && echo "Done."
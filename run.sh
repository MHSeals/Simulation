docker run \
    -it \
    --rm \
    --network=host \
    -v ./src:/root/px4_ros_com_ros2/src
    roboboat bash

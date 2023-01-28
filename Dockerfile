FROM osrf/ros:foxy-desktop-focal

ARG debian_frontend=noninteractive

SHELL [ "/bin/bash", "-c" ]

RUN cp /etc/apt/sources.list /etc/apt/sources.list.backup && \
    sed -i -r 's,http://(.*).ubuntu.com,http://mirror.us-tx.kamatera.com,' /etc/apt/sources.list

# Install packages
RUN apt update && \
    apt -y install python3-colcon-common-extensions ros-foxy-eigen3-cmake-module python3-dev python3-pip python3-pandas python-is-python3 git curl wget build-essential && \
    pip install mavsdk

ENV HOME /root
ENV WORKSPACE ${HOME}/px4_ros_com_ros2
ENV ROSSRC ${WORKSPACE}/src

# Set up the build environment
RUN export PATH="${PATH}:${HOME}/.local/bin" && \
    mkdir -p ${ROSSRC} && \
    git clone https://github.com/PX4/px4_ros_com.git ${ROSSRC}/px4_ros_com && \
    git clone https://github.com/PX4/px4_msgs.git ${ROSSRC}/px4_msgs && \
    git clone https://github.com/PX4/PX4-Autopilot.git --recursive ${ROSSRC}/PX4-Autopilot && \
    bash /${ROSSRC}/px4_ros_com/scripts/build_ros2_workspace.bash && \
    bash ${ROSSRC}/PX4-Autopilot/Tools/setup/ubuntu.sh

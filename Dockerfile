# see https://github.com/PX4/PX4-containers#container-hierarchy
FROM px4io/px4-dev-simulation-focal

ARG debian_frontend=noninteractive

SHELL [ "/bin/bash", "-c" ]

RUN cp /etc/apt/sources.list /etc/apt/sources.list.backup && \
    sed -i -r 's,http://(.*).ubuntu.com,http://mirror.us-tx.kamatera.com,' /etc/apt/sources.list

# making sure Python is Python 3
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y --no-install-recommends install \
    python3-dev \
    python3-pip \
    python-is-python3

# making sure we have Intel GPU access
RUN apt-get update && \
    apt-get -y --no-install-recommends install \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    mesa-utils \
    mesa-utils-extra

# making sure we have MAVSDK
# see https://mavsdk.mavlink.io/main/en/python/quickstart.html#install
RUN python -m pip install --upgrade pip setuptools wheel testresources mavsdk aioconsole

# clone and prebuild PX4 Autopilot software suite
# clone to /root/px4-autopilot
RUN git clone --recurse-submodules -j4 -b v1.13.2 https://github.com/PX4/PX4-Autopilot.git /root/px4-autopilot && \
    cd /root/px4-autopilot && \
    make -j4 px4_sitl_default

# this is so our container will always cd straight to ~
# which is /root because we are running as root
RUN echo "cd /root" >> ~/.bashrc

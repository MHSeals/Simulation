# Simulation

This repository contains code to simulate the boat using Gazebo.


## Pre-Requisite
- [ ] You've set up Docker following the [guide](https://github.com/MHSeals/px4-roboboat)
- [ ] You cloned the repository `git clone https://github.com/MHSeals/Simulation`


## Building and Running the Docker Image
1. Build the docker image

```shell
chmod +x ./build.sh #run this once :D
./build.sh
```

2. Run the docker image

```shell
chmod +x ./run.sh # Run this once :D 
./run.sh
```

Once you're in the container, you can start up the gazebo simulation of the boat

```
cd ${ROSSRC}/PX4-Autopilot
make px4_sitl gazebo_boat
```

## Development
You can connect VSCode to the running docker container and develop live from there!

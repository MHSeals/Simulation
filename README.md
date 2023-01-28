# Simulation

This repository contains code to simulate the boat using Gazebo.

## Pre-Requisite
- [ ] You've set up Docker following the [guide](https://github.com/MHSeals/px4-roboboat)
- [ ] You cloned the repository `git clone https://github.com/MHSeals/Simulation`

## Building and Running the Docker Image

### 1. Build the image

```console
user@host:~$ cd /path/to/this/repository

user@host:~$ bash build.sh
```

Let this run undisturbed. Should now throw an error.

### 2. Execute the container

You need a minimum 2 terminals open.

#### Terminal 1

You will need to create a container. To do this, simply run

```console
user@host:~$ ./run.sh
[sha digest of container]
```

The container is now created and started in background. To attach to it, simply run the script again.

Notice, your username should now be `root`!

```console
user@host:~$ ./run.sh
non-network local connections being added to access control list
Attaching to running roboboat-container container...
root@host:~#
```

Verify that you have access to Intel Graphics as OpenGL Renderer

```console
root@host:~# glxinfo | grep "OpenGL"
```

If you do not see the output similar to above, and renderer is `llvmpipe`, the simulation should still run, but at a
much slower framerate because it is rendering on CPU only. We will fix it later. If this happens, circumvent by running
Gazebo in headless mode. You will not get any visual feedback, but QGroundControl should still behave as if a boat is
present.

You can now build and start the simulation!

```console
root@host:~# cd px4-autopilot
root@docker-desktop:~/px4-autopilot# make -j4 px4_sitl_default gazebo_boat
```

#### Terminal 2 -> Terminal n

Terminal 1 sole purpose is to keep the simulator alive. Any subsequent interaction would need to be on a separate
terminal. The script is designed so that it will attach to the correct container automatically.

Simply run `run.sh` again from the directory of *this* repository.

```console
user@host:~$ ./run.sh
non-network local connections being added to access control list
Attaching to running roboboat-container container...
root@host:~#
```

## Development
You can connect VSCode to the running docker container and develop live from there!

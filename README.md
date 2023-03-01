# Roboboat Simulator

## READ BEFORE CONTINUE

> ⚠️ **MAKE SURE** you build the **correct image AND run commands**!

Files ending with `.[host_os]-[gpu]` should match your system availability.

For example, the companion Zotac PC only has an Intel GPU with Ubuntu on it, so use the `Dockerfile.linux-intel` file when building!

By default, these are now build with no NVIDIA GPU support, and their run scripts do not account for `nvidia-docker2` either!

## Building

Make the script executable and run with `./script_name` if you want...

```console
> cd /path/to/cloned/dir/
> cd Docker
> bash build.sh
```

## Running

Assuming you build the correct image, which should be named `roboboat:simulator-intel` by default, run

```console
> bash run.sh
```

This will start a container in background. Check with `docker ps`.

Subsequent run of the same script will either start the container if not started, or attach to it and give you an internal `bash` prompt.

```console
> bash run.sh
root@host:~#
```

## Develop

There are two primary thing you want to know

1. The `roboboat-code` directory, which stores sample Python programs.
2. The `roboboat-model` directory, which have scripts that spawns the correct boat and environment.

Both are located under `/root/src`

To start the environment, run `bash /root/src/roboboat-model/spawn_env.sh`

To spawn the buoy for Task 1 in the Roboboat 2022 Manual, in a separate terminal, run `python /root/src/roboboat-code/spawn_buoys.py`

![demo](demo-optimized.mp4)
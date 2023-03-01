#!/usr/bin/env bash

# docker build -t roboboat:simulator-nvidia -f Dockerfile.linux-nvidia .

docker build -t roboboat:simulator-intel -f Dockerfile.linux-intel .

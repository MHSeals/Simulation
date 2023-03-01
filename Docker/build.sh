#!/usr/bin/env bash

docker build -t mhseals/roboboat-simulation:linux-nvidia -f Dockerfile.linux-nvidia .

docker build -t mhseals/roboboat-simulation:linux-intel -f Dockerfile.linux-intel .

docker push mhseals/roboboat-simulation:linux-intel

docker push mhseals/roboboat-simulation:linux-nvidia

#!/bin/bash
# full restart
cd /home/ml/.bittensor/subtensor && \
/usr/bin/docker compose down && \
docker system prune -a -f && \
git -C ~/.bittensor/subtensor pull origin master && \
docker pull opentensorfdn/subtensor && \
/usr/bin/docker compose up -d

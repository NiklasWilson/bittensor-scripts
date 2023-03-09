#!/bin/bash
cd /home/ml/.bittensor/subtensor && \
/usr/bin/docker compose down && \
/usr/bin/docker compose up -d

#!/bin/bash
sudo docker logs --follow --since=1h node-subtensor 2>&1  | grep -v -i "accepted"

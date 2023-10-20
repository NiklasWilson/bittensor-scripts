#!/bin/bash

wallet_name=$1
miner_number=$2

while true; do
  #random_number=$((RANDOM % 3001))
  #random_number=$(shuf -i 500-599 -n 1)
  #random_number=500

  # Pad the number with leading zeros to ensure it's always 3 characters
  #i=$(printf "%03d" "$random_number")
  i=$(printf "%03d" "$miner_number")

  echo "registering miner$i"

  btcli s recycle_register --wallet.name $wallet_namne --wallet.hotkey miner$i --netuid 5 --subtensor.network finney

  #Add a delay between iterations
  sleep 5
done
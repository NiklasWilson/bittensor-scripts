#!/bin/bash

num_processes=25

wallet_name = $1

while true; do
  # Generate a random number between 0 and 1000
  random_number=$((RANDOM % 3001))

  # Pad the number with leading zeros to ensure it's always 3 characters
  i=$(printf "%03d" "$random_number")

  echo "registering miner$i"

  btcli subnet register --neuron.device cuda:0 --netuid 5 --wallet.name $wallet_name --wallet.hotkey miner$i --register.verbose  --subtensor.network finney --register.num_processes 90 --no_prompt

  #Add a delay between iterations
  sleep 5
done

#!/bin/bash

wallet_name=$1
# Infinite loop
while true
do
    btcli wallet overview --wallet.name $wallet_name
# Optional: sleep for a while
    sleep 60
done

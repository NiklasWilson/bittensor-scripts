#!/bin/bash
DEV_ID=0
HOTKEY="test-miner1"
MODEL="dataset_wikitext_tuned"
NETWORK="nobunaga"
AXON_PORT=8901

wallet_name = $1

btcli run \
        --cuda \
        --cuda.TPB 512 \
        --cuda.update_interval 70_000 \
        --wallet.name $wallet_name \
        --cuda.dev_id $DEV_ID \
        --logging.trace \
        --logging.record_log bt.log \
        --wallet.hotkey $HOTKEY \
        --subtensor.network=$NETWORK \
        --neuron.model_name=/root/clm_model_tuning/$MODEL \
        --neuron.device cuda:$DEV_ID \
        --neuron.autocast \ 
        --neuron.blacklist.stake 1024 \
        --neuron.backlist.time 150 \
        --logging.debug \
        --wandb.api_key 0ccac9d4b245475e3d6446896fb19da8a5880589 \
        --wandb.project bittensor \
        --wandb.run_group $HOTKEY \
        --axon.port $AXON_PORT
    

        #--subtensor.network local \      
        #--no_prompt \
        #--subtensor.chain_endpoint 207.178.107.92:9944 \
        #--subtensor.chain_endpoint 10.10.10.189:9944 \
        #Model from https://huggingface.co/models?sort=likes
        # --neuron.model_name runwayml/stable-diffusion-v1-5
        #Model from https://huggingface.co/models?sort=downloads
        # --neuron.model_name bert-base-uncased
        # Specify tuned model
        # -neuron.model_name=/home/{YOUR_USENAME}/clm_model_tuning/tuned-model

#!/bin/bash
btcli run \
        --cuda \
        --cuda.TPB 512 \
        --cuda.update_interval 80_000 \
        --subtensor.network local \
        --wallet.name MassedCompute \
        --wallet.hotkey miner1 \
        --cuda.dev_id 0 1 2 3 4 5 6 7 \
        --subtensor.chain_endpoint 10.10.10.189:9944 \
        --no_prompt \
        --logging.debug \
        --neuron.device cuda
        #--subtensor.register.cuda.use_cuda  --subtensor.register.cuda.dev_id 0 1 2 3 4 5 6 7
        #--neuron.model_name=/home/ml/clm_model_tuning/model_distilgpt2_trained 
        
                                                                                        #Model from https://huggingface.co/models?sort=likes
#       --neuron.model_name runwayml/stable-diffusion-v1-5
#Model from https://huggingface.co/models?sort=downloads
        #--neuron.model_name bert-base-uncased
        #Specify tuned model
                # -neuron.model_name=/home/{YOUR_USENAME}/clm_model_tuning/tuned-model

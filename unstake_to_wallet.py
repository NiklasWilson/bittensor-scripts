import pexpect
import sys
import argparse
import os
from dotenv import load_dotenv
import utils

# get wallet into json
wallet = utils.get_wallet()

# for each miner, unstake any amount over 1
# iterate over wallet for each hotkey
for miner in wallet['miners']:
    # If the hotkey is a miner unstake
    if miner['VTRUST']==0.0 and miner['STAKE'] > 1:
        utils.unstake_tokens(miner['HOTKEY'])
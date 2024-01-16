import os
import utils
import json

MAX_STAKE = float(os.getenv("MAX_STAKE")) or 1.0
STAKE_LEFT = True

# get wallet into json
wallet = utils.get_wallet()

print(json.dumps(wallet, indent=2))

initial_amount_staked = wallet["staked_tao"]
initial_wallet_balance = wallet["wallet_balance"]

final_amount_staked = 0.0
final_wallet_balance = 0.0

while STAKE_LEFT:
    STAKE_LEFT = False

    # for each miner, unstake any amount over MAX_STAKE
    # iterate over wallet for each hotkey
    for miner in wallet["miners"]:
        # If the hotkey is a miner unstake
        if miner["VTRUST"] == 0.0 and miner["STAKE"] > MAX_STAKE:
            utils.unstake_tokens(miner["HOTKEY"])
            STAKE_LEFT = True

    print(f"*** Getting wallet - {STAKE_LEFT=}")
    wallet = utils.get_wallet()

final_amount_staked = wallet["staked_tao"]
final_wallet_balance = wallet["wallet_balance"]

print(
    f"{initial_amount_staked=}, {initial_wallet_balance=}, {final_amount_staked=}, {final_wallet_balance=}"
)
print(f"amount staked delta={initial_amount_staked-final_amount_staked}")
print(f"wallet_balance delta={final_wallet_balance-initial_wallet_balance}")

tao_earned = (final_wallet_balance + final_amount_staked) - (
    initial_amount_staked + initial_wallet_balance
)
print(f"tao_earned = {tao_earned}")

import os
import utils
import json
from logging_config import logging
import argparse

max_stake = json.loads(os.getenv("MAX_STAKE"))

logging.info(f"max_stake={max_stake}")
logging.debug(f"max_stake={max_stake}")

final_amount_staked = 0.0
final_wallet_balance = 0.0


def main():
    """
    Main function to be executed when the script is run.
    """

    # get wallet into json
    wallet = utils.get_wallet()

    initial_amount_staked = wallet["staked_tao"]
    initial_wallet_balance = wallet["wallet_balance"]

    logging.info(json.dumps(wallet, indent=2))

    for miner in wallet["miners"]:
        print(f"{miner=}")
        print(f"miner['SUBNET]={miner['SUBNET']}")

    # while there are still tokens to unstake
    STAKE_LEFT = True
    while STAKE_LEFT:
        # set STAKE_LEFT to False to break the loop
        STAKE_LEFT = False

        # for each miner, unstake any amount over the value for the subnet
        # iterate over wallet for each hotkey
        for miner in wallet["miners"]:
            logging.debug(f"{miner=}")

            # get the max stake for the subnet in a string to be used as a key
            subnet_str = str(miner["SUBNET"])
            logging.info(f"max_stake(miner['SUBNET'])={max_stake[subnet_str]}")

            # If the hotkey has more tokens staked than the max for the subnet
            if miner["VTRUST"] == 0.0 and miner["STAKE"] > float(max_stake[subnet_str]):
                logging.info(
                    f"{miner['HOTKEY']} on subnet {subnet_str} has {miner['STAKE']} tokens staked - unstaking {miner['STAKE']-float(max_stake[subnet_str])} tokens"
                )
                utils.unstake_tokens(miner["HOTKEY"], max_stake[subnet_str])

                # set STAKE_LEFT to True to continue the loop
                STAKE_LEFT = True

        logging.info(f"*** Getting wallet - {STAKE_LEFT=}")
        wallet = utils.get_wallet()

    final_amount_staked = wallet["staked_tao"]
    final_wallet_balance = wallet["wallet_balance"]

    logging.info(
        f"{initial_amount_staked=}, {initial_wallet_balance=}, {final_amount_staked=}, {final_wallet_balance=}"
    )
    logging.info(f"amount staked delta={initial_amount_staked-final_amount_staked}")
    logging.info(f"wallet_balance delta={final_wallet_balance-initial_wallet_balance}")

    tao_earned = (final_wallet_balance + final_amount_staked) - (
        initial_amount_staked + initial_wallet_balance
    )
    logging.info(f"tao_earned = {tao_earned}")


if __name__ == "__main__":
    main()

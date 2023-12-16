import utils
import os
import argparse

WALLET_NAME = os.getenv("WALLET_NAME")


if __name__ == "__main__":

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script to generate hotkeys for the bittensor network")

    # Add arguments to the parser
    parser.add_argument('--netuid', type=int, required=True, help='Netuid to create keys for')

    # Parse the arguments from the command line
    args = parser.parse_args()

    netuid=args.netuid
        
    try:
        utils.generate_keys(WALLET_NAME,netuid)
    except Exception as e:
        print (f"Exception trying to generate keys - {str(e)}")
        

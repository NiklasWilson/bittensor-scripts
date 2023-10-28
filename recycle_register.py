import pexpect
import re
import sys
import argparse
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

WALLET_NAME = os.getenv("WALLET_NAME")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")


# Function to safely convert string to float
def safe_float(s):
    try:
        return float(s)
    except ValueError:
        return None

# Set the standard output encoding to UTF-8.
# This will ensure that print can handle the non-ASCII characters.
sys.stdout.reconfigure(encoding='utf-8')

def recycle_register(wallet_name, threshold, hotkey,netuid):
    # Command to run
    command = f'btcli s recycle_register --wallet.name {wallet_name} --wallet.hotkey {hotkey} --netuid {netuid} --subtensor.network finney'

    # Start the process
    child = pexpect.spawn(command)

    # Enable logging to standarad output
    child.logfile_read = sys.stdout.buffer

    # Expect balance and cost information
    child.expect(r"Your balance is: .*?(\d+\.\d+).*The cost to register by recycle is .*?(\d+\.\d+)", timeout=120)
    
    # # Extract the floating point number
    current_wallet = safe_float(child.match.group(1).decode("utf-8"))

    
    #child.expect(r"The cost to register by recycle is .(\d+\.\d+)", timeout=120) 

    # Extract the floating point number
    current_burn = safe_float(child.match.group(2).decode("utf-8"))
    # Expecting the confirmation prompt    
    child.expect(r"Do you want to continue.*", timeout=15)

    #"Do you want to continue\? \[y/n\] \(n\):"

    # Decision based on current_burn
    if current_burn < threshold and current_burn < current_wallet:
        child.sendline("y")
    else:
        child.sendline("n")
        print (f"\ncurrent_burn: {current_burn}  > threshold: {threshold} exceeded, or current_burn: {current_burn} > current_wallet: {current_wallet}")
        child.close()
        return

    # # Expecting password prompt
    child.expect(r"Enter password to unlock key.*", timeout=120)
    child.sendline(WALLET_PASSWORD)  # Sending password

    # # Expect recycle confirmation with cost
    recycle_regex = r"Recycle .*(\d+\.\d+) to register on subnet:.*"
    child.expect(recycle_regex, timeout=120)

    # # Extract the number and make decision
    recycle_cost = safe_float(child.match.group(1).decode("utf-8"))
    print (f"recycle_cost: {recycle_cost}")

    if recycle_cost is not None and recycle_cost < threshold:
        child.sendline("y")
    else:
        print (f"recycle_cost: {recycle_cost} > threshold {threshold}")
        child.sendline("n")

    #child.terminate(force=True)
    # # You might want to add additional code to handle the output or result of the command.
    # # Also, consider error handling for unexpected output or errors in the command execution.

    # # Finally, to ensure the child process is terminated and resources are freed, you can call the close method.
    # To capture the final state/output, you might want to wait for the command to complete execution
    child.expect(pexpect.EOF, timeout=120)

    # Close the child process
    child.close()
    return

if __name__ == "__main__":

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script to accept additional options.")

    # Add arguments to the parser
    parser.add_argument('--netuid', type=int, required=True, help='An integer representing the NetUID.')
    parser.add_argument('--threshold', type=float, required=True, help='A string representing the wallet name.')
    parser.add_argument('--hotkey', type=str, required=True, help='A string representing the wallet name.')

    # Parse the arguments from the command line
    args = parser.parse_args()

    hotkey=args.hotkey
    netuid=args.netuid
    threshold=args.threshold
    
    while True:
        try:
            recycle_register(WALLET_NAME, threshold, hotkey, netuid)
        except Exception as e:
            print (f"Exception trying to register {hotkey} on netuid: {netuid} - {str(e)}")
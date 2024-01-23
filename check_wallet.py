import re
import subprocess
import utils
import datetime
import os
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()

# Access the variables from the .env file
WALLET_NAME = os.getenv("WALLET_NAME")
RANK_THRESHOLD = 0.00350


def is_integer(n):
    try:
        # Attempt to convert the string to an integer
        int(n)
        return True
    except ValueError:
        # If a ValueError is raised, the conversion failed, meaning the string is not an integer
        return False


def get_wallet_data(walletName=WALLET_NAME):
    command = f"btcli w overview --wallet.name {walletName}"

    output = None

    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        )
        print("Output:")
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    # data = """
    # ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    # ┃ 🥩 alert 
    # ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    # │ Found τ273.754804518 stake with coldkey 5GCcbhago4FM6VQQqqMzjfHLHEfhHhjv5GVnDUMnVLUn1F8i that is not registered. │
    # └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
    #                                                                      Wallet - team42:5GCcbhago4FM6VQQqqMzjfHLHEfhHhjv5GVnDUMnVLUn1F8i
    # Subnet: 5
    # COLDKEY  HOTKEY    UID  ACTIVE   STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                HOTKEY_SS58
    # team42   miner501  219    True   19.35835  0.00035  0.20877    0.00050    0.00035    0.00000       33_559  0.00000                71  64.247.206.91:3501  5E7eREyX4fxm1JN6N85795d55UC5TXcmkjzMbFFcgLDYkPYj
    # 1        1         1            τ19.35835  0.00035  0.20877    0.00050    0.00035    0.00000      ρ33_559  0.00000
    #                                                                                       Wallet balance: τ50.336368994
    # """

    subnet_data = []

    if output and output is not None:
        lines = output.strip().split("\n")

        # Get the starting lines
        header_line = 0
        data_line = 0
        for i, line in enumerate(lines):
            if "Wallet" in line:
                header_line = i + 2
                data_line = i + 3
                break
        if header_line == 0 or data_line == 0:
            raise Exception("couldn't determine header or data lines")

        header = [x.strip() for x in lines[header_line].split()]

        subnet=-1
        foundWallet=False
        for line in lines[:-2]:
            if not foundWallet:
                if "Wallet" in line:
                    foundWallet=True
                continue
            if "Subnet" in line:
                subnet = int(line.split(":")[1].strip())
                continue

            parts = re.split(r"\s+", line.strip())

            if len(parts) > 2:
                if "K" in parts:
                    parts.remove("K")

                if "M" in parts:
                    parts.remove("M")

                if "T" in parts:
                    parts.remove("T")

                if len(parts) > 3 and is_integer(parts[2]):
                    subnet_info = {
                        header[0]: parts[0],
                        header[1]: parts[1],
                        header[2]: parts[2],
                        header[3]: parts[3],
                        header[4]: parts[4],
                        header[5]: parts[5],
                        header[6]: parts[6],
                        header[7]: parts[7],
                        header[8]: parts[8],
                        header[9]: parts[9],
                        header[10]: parts[10],
                        header[11]: parts[11],
                        header[12]: parts[12],
                        "SUBNET": subnet
                    }
                    print(subnet_info)
                    subnet_data.append(subnet_info)
    return subnet_data


if __name__ == "__main__":
    # Get the current time
    stored_time = None

    while True:
        wallet_data = get_wallet_data()

        # warn if any of the INCENTIVE < 350

        if wallet_data:
            for item in wallet_data:
                print(f"Comparing rank: {item['RANK']} to threshold {RANK_THRESHOLD} ")
                if float(item["RANK"]) < RANK_THRESHOLD:
                    # Get the current time again
                    current_time = datetime.datetime.now()

                    subject = "LOW RANK Alert"
                    body = f"RANK for {item['HOTKEY']} Is at {item['RANK']} below {RANK_THRESHOLD}"

                    if stored_time is not None:
                        time_difference = current_time - stored_time
                        # Check if the time difference is at least 5 minutes
                        if (
                            time_difference.total_seconds() >= 15 * 60
                        ):  # 5 minutes in seconds
                            utils.send_email(subject, body)

                            # update the stored time
                            stored_time = current_time
                    else:  # first time through
                        utils.send_email(subject, body)

                        # update the stored time
                        stored_time = current_time

        # TODO: Account for error "Error: {'code': -32000, 'message': 'Client error: Execution failed: failed to instantiate a new WASM module instance: maximum concurrent instance limit of 32 reached'}"

        # if subnets_data:
        #     for item in subnets_data:
        #         if item["NETUID"] == 5:
        #             print(f"item_burn: {item['BURN']}")
        #             if item["BURN"] < BURN_THRESHOLD:
        #                 # Get the current time again
        #                 current_time = datetime.datetime.now()

        #                 if stored_time is not None:
        #                     time_difference = current_time - stored_time
        #                     # Check if the time difference is at least 5 minutes
        #                     if (
        #                         time_difference.total_seconds() >= 15 * 60
        #                     ):  # 5 minutes in seconds
        #                         subject = "Bittensor Burn Alert"
        #                         body = f"Burn rate on NetUD 5 is {item['BURN']}"
        #                         utils.send_email(subject, body)

        #                         # update the stored time
        #                         stored_time = current_time
        #                 else:  # first time through
        #                     subject = "Bittensor Burn Alert"
        #                     body = f"Burn rate on NetUD 5 is {item['BURN']}"
        #                     utils.send_email(subject, body)

        #                     # update the stored time
        #                     stored_time = current_time

        # time.sleep (60)

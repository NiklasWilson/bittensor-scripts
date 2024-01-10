"""_summary_
"""
import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json
import subprocess
import subprocess

# import subprocess
import pexpect
import sys
import re
import time
from dotenv import load_dotenv
from string import Template


# Load the environment variables from the .env file
load_dotenv()

# Access the variables from the .env file
email_sender = os.getenv("EMAIL_SENDER")
email_recipients = json.loads(os.getenv("EMAIL_RECIPIENTS"))
email_password = os.getenv("EMAIL_PASSWORD")
WALLET_NAME = os.getenv("WALLET_NAME")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")
SUBTENSOR_ENDPOINT = os.getenv("SUBTENSOR_ENDPOINT")
MAX_STAKE = os.getenv("MAX_STAKE")

wallet_overview_command = Template(f"btcli wallet overview --wallet.name {WALLET_NAME}  --subtensor.network local --subtensor.chain_endpoint {SUBTENSOR_ENDPOINT}")


unstake_token_command = Template(
    f"btcli stake remove --wallet.name {WALLET_NAME} --wallet.hotkey $wallet_hotkey --max_stake {MAX_STAKE} --subtensor.network local --subtensor.chain_endpoint {SUBTENSOR_ENDPOINT}"
)


def send_email(subject: str, body: str) -> bool:
    """
    Sends an email with the given subject and body.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.

    Returns:
        None

    Raises:
        SMTPException: If there is an error while sending the email.

    Examples:
        >>> Utils.send_email("Hello", "This is the body of the email.")
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = ", ".join(email_recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(email_sender, email_password)
        smtp_server.sendmail(email_sender, email_recipients, msg.as_string())

    print(f"{datetime.datetime.now()} Message sent!")

    return True


def is_integer(n):
    try:
        # Attempt to convert the string to an integer
        int(n)
        return True
    except ValueError:
        # If a ValueError is raised, the conversion failed, meaning the string is not an integer
        return False


def get_wallet() -> dict | None:
    """
    Retrieves the wallet with the given name and password.

    Args:
        wallet_name: The name of the wallet.
        wallet_password: The password of the wallet.

    Returns:
        Wallet: The retrieved wallet.

    Examples:
        >>> utils = Utils()
        >>> wallet = utils.get_wallet("MyWallet", "password")
    """

    #command = f"stty cols 180 && btcli w overview --wallet.name {WALLET_NAME} "

    command = wallet_overview_command.substitute(WALLET_NAME=WALLET_NAME, SUBTENSOR_ENDPOINT=SUBTENSOR_ENDPOINT)
    print (f"{command=}")
    
    wallet = {"miners": []}

    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        )
        # print("Output:")
        # print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    lines = output.strip().split("\n")

    subnet = 0

    for line in lines:
        parts = re.split(r"\s+", line.strip())

        if len(parts) > 2:
            if "K" in parts:
                parts.remove("K")

            if "M" in parts:
                parts.remove("M")

            if "T" in parts:
                parts.remove("T")

        # print(f"{parts=}")

        # subnet section - get the subnet number
        if parts[0] == "Subnet:":
            subnet = parts[1]

        # miner line
        if parts[0] == "8thtry":
            miner = {
                "SUBNET": int(subnet),
                "HOTKEY": parts[1],
                "UID": int(parts[2]),
                "ACTIVE": parts[3],
                "STAKE": float(parts[4]),
                "RANK": float(parts[5]),
                "TRUST": float(parts[6]),
                "CONSENSUS": float(parts[7]),
                "INCENTIVE": float(parts[8]),
                "DIVIDENDS": float(parts[9]),
                "EMISSION": float(parts[10]),
                "VTRUST": float(parts[11]),
            }

            # if this is a validator
            if len(parts) == 16:
                miner["VPMERMIT"] = True
                miner["UPDATED"] = int(parts[13])
                miner["AXON"] = parts[14]
                miner["HOTKEY_SS58"] = parts[15]
            else:
                miner["VPMERMIT"] = False
                miner["UPDATED"] = int(parts[12])
                miner["AXON"] = parts[13]
                miner["HOTKEY_SS58"] = parts[14]

            wallet["miners"].append(miner)

            # print(f"{miner=}")

        # final stake line
        if len(parts) == 11:
            # print(f"stake line {parts=}")
            wallet["staked_tao"] = float(
                parts[3][1:]
            )  # remove the first character from the tao

        if parts[0] == "Wallet" and parts[1] == "balance:":
            # print(f"balance line {parts=}")
            wallet["wallet_balance"] = float(
                parts[2][1:]
            )  # remove the first character from the tao

    # print(f"{json.dumps(wallet)}")
    return wallet


# Function to safely convert string to float
def safe_float(s):
    try:
        return float(s)
    except ValueError:
        return None


def unstake_tokens(wallet_hotkey: str) -> bool:
    command = unstake_token_command.substitute(wallet_hotkey=wallet_hotkey)

    try:
        print(f"running {command=}")
        # Start the process
        child = pexpect.spawn(command)

        # Enable logging to standarad output
        child.logfile_read = sys.stdout.buffer

        # Expect balance and cost information
        child.expect("Do you want to unstake from the following keys to .*")
        # print("\nMatched prompt -unstake", child.match.group().decode())
        child.expect(r"(.*)", timeout=120)
        # child.expect("- miner741:5DV5AmHvtruMKirBaTU15625zLnjWxWyjbZ2vaRecqmnYb6f: ")
        # print("\nMatched prompt -miner:", child.match.group().decode())
        # child.expect(r"(^\d+\.\d+e-\d+ .*$)")
        child.expect(r"(.*)")
        # print("\nMatched prompt digits:", child.match.group().decode())
        child.expect(r"(.*)", timeout=120)
        # print("\nMatched prompt [y/n]:", child.match.group().decode(), "sending y")
        child.sendline("y")

        # Expecting password prompt
        child.expect(r"Enter password to unlock key:", timeout=120)
        # print("\nMatched prompt:", child.match.group().decode(), "sending password")
        child.sendline(WALLET_PASSWORD)  # Sending password

        # Expect confirmation:
        child.expect("(Do you want to unstake:)")
        # print("\nMatched prompt:", child.match.group().decode())
        child.sendline("y")

        # Wait for the command to finish and print the output
        child.expect(pexpect.EOF)
        # print(child.before.decode())

    except Exception as e:
        print(f"Error unstaking tokens: {e}")
        return False

    time.sleep(
        10
    )  # if we make requests too fast we get a "TxRateLimitExceeded" - need to look for that string and retry

    return True


def generate_html(data, staked_tao, wallet_balance):
    html = "<!doctype html>\n<html>\n"
    html += """
    <head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    </head>
    """
    html += "<body>\n"
    html += """
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    """
    subnet = None
    first_table = True
    html += "<table table-striped table-hover>\n"

    # # Create table headers
    # html += "<tr>\n"
    # for key in data[0].keys():
    #     html += f"<th>{key}</th>\n"
    # html += "</tr>\n"

    # # Create table rows
    # html += "<tr>\n"
    for item in data:
        for key in item:
            if key == "SUBNET" and item[key] != subnet:
                # print(f"new subnet")
                if not first_table:
                    html += "</tr>"
                    html += "</table>"
                    first_table = False

                subnet = item[key]
                html += """<table class="table table-striped table-hover">"""

                html += """<thead class="thead-dark">\n"""
                html += "<tr>\n"
                for hkey in data[0].keys():
                    # print(f"{hkey=}")
                    html += f"""<th scope="col">{hkey}</th>\n"""
                html += "</tr>\n"
                html += "</thead>\n"

                html += """<tbody class="table-group-divider">"""
            # print(f"{item[key]=}")
            html += f"<td>{item[key]}</td>\n"
        html += "</tr>\n"

    html += "</table>\n"

    # End table
    html += "<table>\n"
    html += "<tr>\n"
    html += f"<td>Staked Tao:</td><td>{staked_tao}</td>\n"
    html += "</tr>\n"
    html += "<tr>\n"
    html += f"<td>Wallet Balance:</td><td>{wallet_balance}</td>\n"
    html += "</tr>\n"
    html += "</table>\n"
    now = datetime.datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")

    html += "<p>&nbsp;</p>"
    html += f"""<p class="font-italic">last updated: {dt_string}</p>"""
    html += "</body>\n</html>"

    return html

def generate_keys(wallet:str, netuid: int):
    """
    Prints the iteration numbers from 00 to 99, each prepended by the given netuid.
    Each iteration number is zero-padded to ensure it is always two characters.
    
    :param netuid: The netuid to prepend to each iteration number.
    """
    for i in range(100):
        # Format the iteration number with zero-padding to two digits and prepend the netuid
        command = f"btcli w new_hotkey --wallet.name {WALLET_NAME} --wallet.hotkey miner{netuid}{i:02d}"
        print(f"registering: mminer{netuid}{i:02d}, command: {command}")
        try:
            output = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
            )
            print("Output:")
            print(output)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        


# # get wallet into json
# wallet = Utils.get_wallet()

# # for each miner, unstake any amount over 1
# # # iterate over wallet for each hotkey
# # for miner in wallet['miners']:
# #     # If the hotkey is a miner unstake
# #     if miner['VTRUST']==0.0 and miner['STAKE'] > 1:
# #         Utils.unstake_tokens(miner['HOTKEY'])

# # Sort the list of dictionaries by the age value
# sorted_wallet = sorted(wallet["miners"], key=lambda x: x["SUBNET"])

# # Generate HTML
# html_content = Utils.generate_html(
#     sorted_wallet,
#     wallet_balance=wallet["wallet_balance"],
#     staked_tao=wallet["staked_tao"],
# )

# # print(html_content)
# # # Write HTML to a file
# with open("output.html", "w") as file:
#     file.write(html_content)

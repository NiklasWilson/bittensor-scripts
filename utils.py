"""_summary_
"""
import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json
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
SUBTENSOR_ENDPOINT = "ws://209.137.198.70:9944"  # TOOD: Move to .env

wallet_overview_command = Template(f"btcli wallet overview --wallet.name {WALLET_NAME}")
unstake_token_command = Template(
    f"btcli stake remove --wallet.name {WALLET_NAME} --wallet.hotkey $wallet_hotkey --max_stake 1 --subtensor.network local --subtensor.chain_endpoint {SUBTENSOR_ENDPOINT}"
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

    command = f"stty cols 180 && btcli w overview --wallet.name {WALLET_NAME}"

    wallet = {"miners": []}

    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        )
        print("Output:")
        print(output)
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

        print(f"{parts=}")

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
            print(f"stake line {parts=}")
            wallet["staked_tao"] = float(
                parts[3][1:]
            )  # remove the first character from the tao

        if parts[0] == "Wallet" and parts[1] == "balance:":
            # print(f"balance line {parts=}")
            wallet["wallet_balance"] = float(
                parts[2][1:]
            )  # remove the first character from the tao

    print(f"{json.dumps(wallet)}")
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
        print(child.before.decode())

    except Exception as e:
        print(f"Error unstaking tokens: {e}")
        return False

    time.sleep(
        10
    )  # if we make requests too fast we get a "TxRateLimitExceeded" - need to look for that string and retry

    return True


def generate_html(data, staked_tao, wallet_balance):
    html = "<html>\n"
    html += """
    <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <style>
    </style>
    </head>
    """
    html += "<body>\n"
    html += """<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>"""
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

                html += "<tr>\n"
                for hkey in data[0].keys():
                    # print(f"{hkey=}")
                    html += f"<th>{hkey}</th>\n"
                html += "</tr>\n"
                html += """<tbody class="table-group-divider">"""
            # print(f"{item[key]=}")
            html += f"<td>{item[key]}</td>\n"
        html += "</tr>\n"

    html += "</table>\n"

    # End table
    html += "<table>\n"
    html += "<tr>\n"
    html += f"<td>Staked Tao:</td><td>{staked_tao}</td>\n"
    html += f"<td>Wallet Balance:</td><td>{wallet_balance}</td>\n"
    html += "</tr>\n"
    html += "</table>\n"

    html += "</body>\n</html>"

    return html
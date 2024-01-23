import subprocess
import re
import argparse


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if error:
        raise Exception("Error running command: " + str(error))
    return output.decode("utf-8")


def clean_list(input_list):
    cleaned_list = [value for value in input_list if value and value != ""]
    return cleaned_list


def remove_empty_and_special_characters(input_list):
    cleaned_list = clean_list(input_list)
    return [re.sub(r"[^\w\s]", "", value) for value in cleaned_list]


def addMinerIncome(miner):
    emission = int(miner["EMISSION"]) if "EMISSION" in miner else 0.0
    miner["dailyTAO"] = emission * 0.000000001 * 20
    miner["hourlyTAO"] = miner["dailyTAO"] / 24
    return miner


def parse_output(output):
    lines = output.split("\n")
    metagraphLine = ""
    tableLine = ""
    columns = []
    columnsNoVal = []
    miners = []

    count = -1
    for line in lines:
        count += 1
        print(line)
        if count == 0:
            metagraphLine = line
        elif count == 1:
            tableLine = line
            columns = remove_empty_and_special_characters(
                tableLine.replace("ρ", "").replace("τ", "").split(" ")
            )
            columnsNoVal = [x for x in columns if x != "VAL"]
        else:
            miner = {}
            values = remove_empty_and_special_characters(
                line.replace("ρ", "").replace("τ", "").split(" ")
            )
            for i in range(len(values)):
                if len(values) < len(columns):
                    miner[columnsNoVal[i]] = values[i]
                else:
                    miner[columns[i]] = values[i]
            miner = addMinerIncome(miner)
            miners.append(miner)
    return miners


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallet", type=str, required=True, help="The wallet UID")
    parser.add_argument(
        "--subnets", type=str, nargs="+", help="Comma-separated list of numbers"
    )

    args = parser.parse_args()

    wallet_uid = args.wallet
    subnet_list = [int(x) for x in args.subnets[0].split(",")]

    print(f"Wallet UID: {wallet_uid}")
    print(f"Subnet list: {subnet_list}")

    dailyTao = 0.0
    hourlyTao = 0.0
    for subnet in subnet_list:
        command = f"btcli s metagraph --netuid {subnet} | grep -i -e metagraph -e UID -e {wallet_uid}"
        output = run_command(command)
        miners = parse_output(output)
        dailyTaoSubnet = 0.0
        hourlyTaoSubnet = 0.0
        num_miners = len(miners) - 1
        for miner in miners:
            if "HOTKEY" in miner:
                print(
                    f"HOTKEY {miner['HOTKEY']} is making {miner['hourlyTAO']} TAO/hr and {miner['dailyTAO']} TAO/day"
                )
                dailyTao += miner["dailyTAO"]
                dailyTaoSubnet += miner["dailyTAO"]
                hourlyTao += miner["hourlyTAO"]
                hourlyTaoSubnet += miner["hourlyTAO"]

        hourly_avg = 0
        if hourlyTaoSubnet > 0:
            hourly_avg = hourlyTaoSubnet / num_miners

        daily_avg = 0
        if dailyTaoSubnet > 0:
            daily_avg = dailyTaoSubnet / num_miners

        print(
            f"Subnet {subnet} is making {hourlyTaoSubnet} TAO/hr and {dailyTaoSubnet} TAO/day averaging {hourly_avg} an hour and {daily_avg} a day per miner"
        )

    print(f"Wallet {wallet_uid} is earning {hourlyTao} TAO per hour")
    print(f"Wallet {wallet_uid} is earning {dailyTao} TAO per day")


if __name__ == "__main__":
    main()

from itertools import product
import subprocess
import re
import argparse
import requests
import multiprocessing
import functools

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if error:
        raise Exception("Error running command: " + str(error))
    return output.decode("utf-8")

def clean_list(input_list):
    cleaned_list = [value for value in input_list if value and value != '']
    return cleaned_list

def remove_empty_and_special_characters(input_list):
    cleaned_list = clean_list(input_list)
    return [re.sub(r'[^\w\s]','', value) for value in cleaned_list]

def addMinerIncome(miner):
    emission = int(miner["EMISSION"]) if "EMISSION" in miner else 0.0
    miner["dailyTAO"]=emission * .000000001 * 20
    miner["hourlyTAO"]=miner["dailyTAO"]/24
    return miner

def get_bittensor_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bittensor&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data['bittensor']['usd']
    except Exception as e:
        return f"Error: {e}"

def parse_output(output):
    data = {}
    lines = output.split("\n")
    metagraphLine=""
    tableLine=""
    columns=[]
    columnsNoVal=[]
    miners=[]

    count=-1
    for line in lines:
      count+=1
      print(line)
      if count==0: metagraphLine=line
      elif count==1:
        tableLine=line
        columns=remove_empty_and_special_characters(tableLine.replace('ρ','').replace('τ','').split(' '))
        columnsNoVal=[x for x in columns if x != 'VAL']
      else:
        miner={}
        values=remove_empty_and_special_characters(line.replace('ρ','').replace('τ','').split(' '))
        for i in range(len(values)):
          if len(values) < len(columns):
            miner[columnsNoVal[i]]=values[i]
          else:
            miner[columns[i]]=values[i]
        miner=addMinerIncome(miner)
        miners.append(miner)
    return miners

def getMinersForSubnet(subnet, wallet_uids):
    print(f"Getting miners for subnet {subnet} and wallets {wallet_uids}")
    # Command to get miners for a given subnet for specfied cold keys
    command = f"btcli s metagraph --netuid {subnet} | grep -i -e metagraph -e UID -e {' -e '.join(wallet_uids)}"
    output = run_command(command)
    miners = parse_output(output)
    return miners

def getMinersForSubnets(subnets, wallet_uids):
    # For each subnet run getMinersForSubnet using the multiproccesing library
    with multiprocessing.Pool() as pool:
        miners = pool.map(functools.partial(getMinersForSubnet, wallet_uids=wallet_uids), subnets)
    # Flatten the list of lists
    allMiners = [item for sublist in miners for item in sublist]
    return allMiners

def seperateMinersByWallet(miners):
    # Create a dictionary of miners by wallet
    minersByWallet = {}
    for miner in miners:
        coldkey = miner['COLDKEY'] if "COLDKEY" in miner else "unknown"
        if coldkey in minersByWallet:
            minersByWallet[coldkey].append(miner)
        else:
            minersByWallet[coldkey] = [miner]
    return minersByWallet

def getIncomeByWalletForSubnets(subnet_list, wallet_uids):
    miners = getMinersForSubnets(subnet_list, wallet_uids)
    minersByWallet = seperateMinersByWallet(miners)
    taoPrice = get_bittensor_price()
    wallets = {}
    for wallet_uid in wallet_uids:
        dailyTao=0.0; hourlyTao=0.0
        for miner in minersByWallet[wallet_uid]:
            dailyTao+=miner['dailyTAO']
            hourlyTao+=miner['hourlyTAO']
        wallets[wallet_uid] = {
            "miners": minersByWallet[wallet_uid],
            "dailyTAO": dailyTao,
            "hourlyTAO": hourlyTao,
            "dailyUSD": dailyTao*taoPrice,
            "hourlyUSD": hourlyTao*taoPrice
        }
    return wallets

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallets", type=str, nargs="+", required=True, help="The wallet UIDs")
    parser.add_argument("--subnets", type=str, nargs="+", required=True, help="Comma-separated list of numbers")

    args = parser.parse_args()

    wallet_uids = [x for x in args.wallets[0].split(',')]
    subnet_list = [int(x) for x in args.subnets[0].split(',')]

    print(f"Wallet UID: {wallet_uids}")
    print(f"Subnet list: {subnet_list}")

    wallets = getIncomeByWalletForSubnets(subnet_list, wallet_uids)
    for wallet in wallets:
        print(f"Wallet {wallet} has {len(wallets[wallet]['miners'])} miners")
        print(f"Wallet {wallet} is making {wallets[wallet]['dailyTAO']} TAO/day")
        print(f"Wallet {wallet} is making {wallets[wallet]['hourlyTAO']} TAO/hr")
        print(f"Wallet {wallet} is making ${wallets[wallet]['dailyUSD']} USD/day")
        print(f"Wallet {wallet} is making ${wallets[wallet]['hourlyUSD']} USD/hr")

if __name__ == "__main__":
    main()

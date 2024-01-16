import argparse
from check_burn import get_subnets_data
from check_wallet import get_wallet_data
import utils

def get_subnets(excludeLowEmission=False):
    subnets = {}
    subnets_data = get_subnets_data()
    for subnet in subnets_data:
        subnet_emission = float(subnet["EMISSION"].replace('%',''))
        if excludeLowEmission and subnet_emission <= 0.01:
            continue

        subnets[subnet["NETUID"]] = subnet
        if subnet["BURN"] < 1:
            subnets[subnet["NETUID"]]["minimum_balance"] = 1.5
        elif subnet["BURN"] < 4:
            subnets[subnet["NETUID"]]["minimum_balance"] = round(subnet["BURN"] * 1.5, 2)
        else:
            subnets[subnet["NETUID"]]["minimum_balance"] = round(subnet["BURN"] * 1.1, 2)
        print(f"Subnet {subnet['NETUID']} has minimum balance {subnets[subnet['NETUID']]['minimum_balance']} and a current burn of {subnet['BURN']} and emission of {subnet_emission}")
    return subnets

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallets", type=str, nargs="+", required=True, help="Example mtllc01:5CK1u3qe6ZCHgpcCvGYf2H4acrZBAPam7extoxE6ntk7mymi")
    args = parser.parse_args()

    walletNames = []; walletColdkeys = []
    for pair in args.wallets[0].split(','):
        walletName, walletKey = pair.split(':')
        walletNames.append(walletName)
        walletColdkeys.append(walletKey[:10])

    subnets = get_subnets(excludeLowEmission=False)

    for walletName in walletNames:
        hotkeys = get_wallet_data(walletName)
        for hotkey in hotkeys:
            if hotkey['SUBNET'] in subnets:
                if float(hotkey['STAKE(τ)']) < subnets[hotkey['SUBNET']]['minimum_balance']:
                    print(f"Wallet {walletName} has hotkey {hotkey['HOTKEY']} in subnet {hotkey['SUBNET']} with balance {hotkey['STAKE(τ)']} which is below the minimum balance of {subnets[hotkey['SUBNET']]['minimum_balance']}")
                else:
                    print(f"Will unstake from hotkey {hotkey['HOTKEY']} in subnet {hotkey['SUBNET']} with balance {hotkey['STAKE(τ)']} which is above the minimum balance of {subnets[hotkey['SUBNET']]['minimum_balance']}")
                    utils.unstake_tokens(hotkey['HOTKEY'], subnets[hotkey['SUBNET']]['minimum_balance'], walletName)

if __name__ == "__main__":
    main()
import re
import json
import subprocess
import utils
import time
import datetime

BURN_THRESHOLD = 13

def get_subnets_data():
    command = "btcli s list"

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
    #                                                  Subnets - finney
    #  NETUID   N    MAX_N   EMISSION  TEMPO    BURN         POW       SUDO
    #    0      62   64.00    0.00%     100   τ1.00000     10.00 M     5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM
    #    1     1024  1.02 K   57.96%    99    τ5.75781  1000000.00 T   5Hpd1smgd8tjQYqZ7tuXBxiC85LYivtKwpYAmoXvpJiJghfu
    #    2     170   256.00   0.00%     360   τ0.00000    100.00 T     5HeQuPVRSZVE3LWdKx9q6upyCi53TjQ4a2S8mnJ5emyWFf5b
    #    3     239   256.00   3.24%     360   τ2.02728    100.00 T     5FNBJf6xruFpKNxi7SoQQdedXUpC5nneSMJdzP5pZNpq35iA
    #    4     256   256.00   0.00%     360   τ0.02516    100.00 T     5CXGPMnq9RCCLUEvp9G2iUuabw69TSFM155UVS1S4Zmusaxv
    #    5     256   256.00   24.24%    360   τ27.3683    100.00 T     5HiveMEoWPmQmBAb8v63bKPcFhgTGCmST1TVZNvPHSTKFLCv
    #    6     189   256.00   0.00%     360   τ0.00003     52.39 K     5HiWr9tvNhVc7wp539Gf4Gbe3PC7c8hB7WnC9q4MYj7bqWmq
    #    7     139   256.00   0.00%     360   τ0.00878  18446744.07 T  5DoFgSb8hdVCLAKTXCmd4bTSKHd2mG4QKatpK3DvJR91DVoc
    #    8     104   256.00   0.00%     360   τ0.01977  18446744.07 T  5F6tnxzAAxbhaWRmeUmB63JEM3VXBNSmqb3AwYJVDStQjw8y
    #    9      58   256.00   0.00%     360   τ0.00659  18446744.07 T  5CqPn4g7Q6VsdEmbp2i2Z3nvJWQngCfG7K5kCgzGSPgxynDf
    #    11    2048  2.05 K   14.56%    199   τ0.23187  1000000.00 T   5Hpd1smgd8tjQYqZ7tuXBxiC85LYivtKwpYAmoXvpJiJghfu
    #    11    5184
    # """

    subnet_data = []

    if output and output is not None:
        lines = output.strip().split("\n")
        header = [x.strip() for x in lines[1].split()]

        for line in lines[2:-1]:
            parts = re.split(r"\s+", line.strip())

            if "K" in parts:
                parts.remove("K")

            if "M" in parts:
                parts.remove("M")

            if "T" in parts:
                parts.remove("T")

            # print (f"parts:{parts}")
            subnet_info = {
                header[0]: int(parts[0]),
                header[1]: int(parts[1]),
                header[2]: parts[2],
                header[3]: parts[3],
                header[4]: parts[4],
                header[5]: float(parts[5][1:]),  # Remove 'τ' and convert to float
                header[6]: parts[6],
                header[7]: parts[7],
            }
            subnet_data.append(subnet_info)
    return subnet_data


if __name__ == "__main__":
    # Get the current time
    stored_time = None

    while True:
        subnets_data = get_subnets_data()

        if subnets_data:
            for item in subnets_data:
                if item["NETUID"] == 5:
                    print (f"item_burn: {item['BURN']}")
                    if item["BURN"] < BURN_THRESHOLD:
                        # Get the current time again
                        current_time = datetime.datetime.now()

                        if stored_time is not None:
                            time_difference = current_time - stored_time
                            # Check if the time difference is at least 5 minutes
                            if (
                                time_difference.total_seconds() >= 15 * 60
                            ):  # 5 minutes in seconds
                                subject = "Bittensor Burn Alert"
                                body = f"Burn rate on NetUD 5 is {item['BURN']}"
                                utils.send_email(subject, body)

                                # update the stored time
                                stored_time = current_time
                        else:  # first time through
                            subject = "Bittensor Burn Alert"
                            body = f"Burn rate on NetUD 5 is {item['BURN']}"
                            utils.send_email(subject, body)

                            # update the stored time
                            stored_time = current_time

        # time.sleep (60)

        # print (f"Burn on netuid 5 is < 16")

    # Convert the data to JSON
    # subnet_json = json.dumps(subnet_data, indent=2)

    # Print the JSON data
    # print(subnet_json)

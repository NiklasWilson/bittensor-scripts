import utils

# get wallet into json
wallet = utils.get_wallet()

# Sort the list of dictionaries by the age value
sorted_wallet = sorted(wallet["miners"], key=lambda x: x["SUBNET"])

# print(json.dumps(sorted_wallet, indent=4))

# Generate HTML
html_content = utils.generate_html(
    sorted_wallet,
    wallet_balance=wallet["wallet_balance"],
    staked_tao=wallet["staked_tao"],
)

# print(html_content)
# # Write HTML to a file
with open("output.html", "w") as file:
    file.write(html_content)
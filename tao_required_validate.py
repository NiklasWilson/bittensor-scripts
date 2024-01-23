import bittensor as bt
from pprint import pprint

subnet = bt.metagraph(8)
#pprint(f"{subnet.dir()=}")
pprint(f"{subnet.__dir__()=}")
pprint(f"{vars(subnet)=}")
top_64_stake = subnet.S.sort()[0][-64:].tolist()
print (f'Current requirement for validator permits based on the top 64 stake stands at {min(top_64_stake)} tao')

import re
from datetime import datetime, timedelta

data = """
29|0-miner501-8818-copaxTimelessxlSDXL1_v7  | 2023-10-23T03:09:19: TRACE:    213.224.31.105:34120 - HTTP connection made
"""


def get_last_execute_time():
    parts = re.split(r"\s+", data.strip())

    print (f"parts: {parts}")

    time =parts[2][:-1]

    print (f"time: {time}")

    return time



def has_three_minutes_passed(given_time_str):

    # Define the format the string is in
    time_format = "%Y-%m-%dT%H:%M:%S"
    
    # Parse the given_time_str to a datetime object
    given_time = datetime.strptime(given_time_str, time_format)

    print (f"given_time: {given_time}")
    # Get the current time
    current_time = datetime.now()
    print (f"current_time: {current_time}")

    # Calculate the time difference
    difference = current_time - given_time

    print (f"difference: {difference}")

    # Check if the difference is more than 3 minutes
    if difference > timedelta(minutes=1):
        return True
    else:
        return False

time_str = get_last_execute_time()

# Example usage
if has_three_minutes_passed(time_str):
    print("More than 3 minutes have passed.")
else:
    print("Less than 3 minutes have passed.")

#check for errors
# 37|0-miner | 2023-10-24T13:39:01: Exception: Internal server error with error: Expecting ',' delimiter: line 24 column 13 (char 493)
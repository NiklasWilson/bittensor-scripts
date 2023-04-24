import requests
import json
import ast
import re

pattern = re.compile(r"{\"Name\":\s+\"(.*?)\"\,\s+\"Hash\":\s+\"(.*?)\"\,\s+\"Size\":\s+\d+}")

def get_file(hash):
    """
    Recursively fetches IPFS objects until a file is found and returns the contents of the file.
    """
    # Fetch the IPFS object
    url = f"http://global.ipfs.opentensor.ai/api/v0/object/get?arg={hash}"
    print(f"url: {url}")

    r = requests.post(url)

    # Check if it's a file or a directory
    data = r.json()
    print (f"data: {data}")

    if "Links" in data and len(data['Links']) == 0:
        print (f"** Filenames: {data['Data']} {type(data['Data'])}")
        for (filename,hash) in re.findall(pattern,data['Data']):
            print (f"** Writing filename: {filename}, hash: {hash}")
            url = f"http://global.ipfs.opentensor.ai/api/v0/object/get?arg={hash}"
            r = requests.post(url)

            with open(filename, "w") as f:
                f.write(r.text)
    else:
        if "Links" in data:
            for item in data['Links']:
                if "Hash" in item:
                    # If it's a directory, recurse over the contents
                    return get_file(item["Hash"])

if __name__ == "__main__":

    url = "http://global.ipfs.opentensor.ai/api/v0/object/get?arg=QmSdDg6V9dgpdAFtActs75Qfc36qJtm9y8a7yrQ1rHm7ZX"
    print(f"url: {url}")
    r = requests.post(url)

    data=r.json()
    print(f"initial data: {data}")

    if "Links" in data:
        for item in data['Links']:
            print(f"item: {item} - hash: {item['Hash']}")
            hash=item['Hash']
            file_contents = get_file(hash)

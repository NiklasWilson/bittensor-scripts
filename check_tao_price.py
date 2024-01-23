import os
import re
import smtplib

MAX_PURCAHSE_PRICE = 8.0
GMAIL_APP_PASSWORD = ""
EMAIL = ""
DEBUG = False

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com",
}


def send_message(email, message):
    auth = (EMAIL, GMAIL_APP_PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], email, message)


def send_sms_message(phone_number, carrier, message):
    # https://testingonprod.com/2021/10/24/how-to-send-text-messages-with-python-for-free/
    # https://testingonprod.com/2021/10/24/how-to-send-text-messages-with-python-for-free/
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, GMAIL_APP_PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)


def get_recycle_register_cost():
    # Run btcli to get the current TAO recycle_register cost
    stream = os.popen(
        "btcli recycle_register --wallet.name test --subtensor.network finney --netuid 3 --no_prompt true"
    )
    output = stream.read()

    # The search() function returns a Match object:
    # txt = "Insufficient balance ~D0.000000000 to register neuron. Current recycle is ~D13.275002128 TAO"
    x = re.search(r"[\d\.]+ TAO", output)

    # Get the digit from the match
    txt = x.group()
    x = re.search(r"\d+.\d+", txt)
    current_price = float(x.group())

    return current_price


if __name__ == "__main__":
    current_price = get_recycle_register_cost()
    if DEBUG:
        print(f"current prices {current_price}")

    if current_price < MAX_PURCAHSE_PRICE:
        if DEBUG:
            print(
                f"current price:{current_price} is less than max purchase price:{MAX_PURCAHSE_PRICE}"
            )

        text = f"recycle_register coset is {current_price} BUY BUY BUY!!!"
        subject = "BUY!! BUY!! BUY!!"

        message = f"Subject: {subject}\n\n{text}"

        # phone_number="XXXXXX"
        # carrier="tmobile"

        email = ""

        send_message(email, message)

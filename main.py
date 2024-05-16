"""
Generate one time email addresses for a domain.
One way email addresses are useful for signing up for services without revealing your real email address.
Solves the problem of spam and privacy.
"""
import os
import requests
import random
import time
import hashlib
import smtpd
import asyncore
from sympy import isprime

# Set your bot's API token and your Telegram user ID
SMTP_PORT = int("25")
TG_TOKEN = "6322093150:AAGHQzHg-w6HxaQjkm1F4qUFCybOswTEv7s"
print(TG_TOKEN)
MY_ID = 478921859
LOOP = False

# Define the URL for sending messages via the Telegram Bot API
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

# Define the URL for receiving updates from the Telegram Bot API
GET_UPDATES_URL = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates?timeout=60"

# Define the allowed chat ID
ALLOWED_CHAT_ID = MY_ID

# Define the main email address
MAIN_EMAIL = ""
REDIRECT_IP = ""
MAIN_PRIME = ""
CURRENT_EPOCH = ""
SECRET_HASH = ""
DOMAINS = {}
UPDATE_IDS = []


def generate_large_random_prime(bit_length):
    """
    Generate a large random prime number with the specified bit length.

    Parameters:
        bit_length (int): The desired bit length of the prime number.

    Returns:
        int: A large random prime number.
    """
    while True:
        n = random.getrandbits(bit_length)
        n |= (1 << bit_length - 1) | 1
        if isprime(n):
            return n


def send_message(chat_id, text):
    """
    Send a message to the specified chat ID using the Telegram Bot API.

    Parameters:
        chat_id (int): The ID of the chat where the message should be sent.
        text (str): The text of the message.
    """
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(SEND_MESSAGE_URL, params=params)
    if response.ok:
        print("Message sent successfully!")
    else:
        print("Failed to send message:", response.text)


def get_updates():
    """
    Get updates (messages) from the Telegram Bot API.

    Returns:
        list: A list of updates (messages) received by the bot.
    """
    response = requests.get(GET_UPDATES_URL)
    data = response.json()
    return data["result"]


def get_domain_from_email(email):
    """
    Get the domain from an email address.

    Parameters:
        email (str): The email address.

    Returns:
        str: The domain part of the email address.
    """
    return email.split("@")[1]


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(
        self, peer, mailfrom, rcpttos, data, mail_options=None, rcpt_options=None
    ):
        print(f"Received message from: {mailfrom}")
        domain = get_domain_from_email(mailfrom)
        if domain not in DOMAINS:
            print(f"Domain not found: {get_domain_from_email(mailfrom)}")
            # smtp response for not found domain
            self.push("550 Domain not found")
            return
        # verify hash matches the domain
        time = DOMAINS[domain]
        gen_email = hashlib.sha256(
            MAIN_EMAIL.encode()
            + domain.encode()
            + SECRET_HASH.encode()
            + str(time).encode()
        )
        if "0x" + gen_email.hexdigest() not in rcpttos:
            print(f"Invalid email: {mailfrom}")
            # smtp response for invalid email
            self.push("550 Invalid email")
            return
        else:
            # forward the email to the main email
            print(f"Forwarding email to: {MAIN_EMAIL}")
            with smtplib.SMTP("0.0.0.0", SMTP_PORT) as server:
                server.sendmail(mailfrom, MAIN_EMAIL, data)
            print("Email forwarded successfully!")
            # smtp response for successful email forwarding
            self.push("250 Email forwarded successfully!")
            return


def main():
    # Generate a large random prime number
    bit_length = 1024
    prime_number = generate_large_random_prime(bit_length)
    global MAIN_PRIME
    MAIN_PRIME = prime_number

    # Get current epoch time
    current_time = int(time.time())
    global CURRENT_EPOCH
    CURRENT_EPOCH = current_time

    # Make a hash of the prime number and current epoch time
    hash_object = hashlib.sha256(
        str(prime_number).encode() + str(current_time).encode()
    )
    global SECRET_HASH
    SECRET_HASH = hash_object.hexdigest()

    # Start the SMTP server
    smtp_server = CustomSMTPServer(("0.0.0.0", SMTP_PORT), None)
    print("SMTP server started...", SMTP_PORT)

    # Poll for updates from the Telegram Bot API and process messages
    while True:
        # get updates
        updates = get_updates()
        # get last update
        update = updates[-1:]
        # check if the update ID has already been processed
        update_id = update[0]["update_id"]
        if update_id in UPDATE_IDS:
            continue
        chat_id = update[0]["message"]["chat"]["id"]
        text = update[0]["message"]["text"]
        print(f"Received message from chat ID {chat_id}: {text}")
        if chat_id == ALLOWED_CHAT_ID:
            # Process the message
            print(f"Received message from chat ID {chat_id}: {text}")
            if text.startswith("SET EMAIL"):
                global MAIN_EMAIL
                print('SET EMAIL')
                MAIN_EMAIL = text.split("SET EMAIL ")[1]
                send_message(chat_id, f"Main email set to: {MAIN_EMAIL}")

            if text.startswith("SET REDIRECT"):
                global REDIRECT_IP
                REDIRECT_IP = text.split("SET REDIRECT ")[1]
                send_message(chat_id, f"Redirect IP set to: {REDIRECT_IP}")
            elif text.startswith("ADD DOMAIN"):
                # global DOMAINS
                domain = text.split("ADD DOMAIN ")[1]
                if domain in DOMAINS:
                    send_message(chat_id, f"Domain already exists: {domain}")
                    return
                current_time = int(time.time())
                gen_email = hashlib.sha256(
                    MAIN_EMAIL.encode()
                    + domain.encode()
                    + SECRET_HASH.encode()
                    + str(current_time).encode()
                )
                DOMAINS[domain] = current_time
                print(f"Domain added: {domain}")
                send_message(chat_id, f"0x{gen_email.hexdigest()}@{REDIRECT_IP}")

            elif text.startswith("REMOVE DOMAIN"):
                # global DOMAINS
                domain = text.split("REMOVE DOMAIN ")[1]
                if domain not in DOMAINS:
                    send_message(chat_id, f"Domain does not exist: {domain}")
                    return
                del DOMAINS[domain]
                print(f"Domain removed: {domain}")
                send_message(chat_id, f"Domain removed: {domain}")
        # Add a delay before checking for updates again
        # asyncore.loop()
        UPDATE_IDS.append(update_id)
        time.sleep(1)
    

if __name__ == "__main__":
    main()

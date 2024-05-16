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
TG_TOKEN = os.getenv("TG_TOKEN")
print(TG_TOKEN)
MY_ID = os.getenv("MY_ID")

# Define the URL for sending messages via the Telegram Bot API
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

# Define the URL for receiving updates from the Telegram Bot API
GET_UPDATES_URL = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates"

# Define the allowed chat ID
ALLOWED_CHAT_ID = MY_ID

# Define the main email address
MAIN_EMAIL = ''
MAIN_PRIME = ''
CURRENT_EPOCH = ''
SECRET_HASH = ''
DOMAINS = {}

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
    params = {'chat_id': chat_id, 'text': text}
    response = requests.post(SEND_MESSAGE_URL, params=params)
    if response.ok:
        print('Message sent successfully!')
    else:
        print('Failed to send message:', response.text)

def get_updates():
    """
    Get updates (messages) from the Telegram Bot API.
    
    Returns:
        list: A list of updates (messages) received by the bot.
    """
    response = requests.get(GET_UPDATES_URL)
    data = response.json()
    print(data)
    return data['result']

def get_domain_from_email(email):
    """
    Get the domain from an email address.
    
    Parameters:
        email (str): The email address.
        
    Returns:
        str: The domain part of the email address.
    """
    return email.split('@')[1]


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data,mail_options=None,rcpt_options=None):
        print(f"Received message from: {mailfrom}")
        domain = get_domain_from_email(mailfrom)
        if domain not in DOMAINS:
            print(f"Domain not found: {get_domain_from_email(mailfrom)}")
            # smtp response for not found domain
            self.push('550 Domain not found')
            return
        # verify hash matches the domain
        time = DOMAINS[domain]
        gen_email = hashlib.sha256(MAIN_EMAIL.encode() + domain.encode() + SECRET_HASH.encode() + str(time).encode())
        if '0x' + gen_email.hexdigest() not in rcpttos:
            print(f"Invalid email: {mailfrom}")
            # smtp response for invalid email
            self.push('550 Invalid email')
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
    hash_object = hashlib.sha256(str(prime_number).encode() + str(current_time).encode())
    global SECRET_HASH
    SECRET_HASH = hash_object.hexdigest()

    # Start the SMTP server
    smtp_server = CustomSMTPServer(('0.0.0.0', 465), None)
    print("SMTP server started...")

    # Poll for updates from the Telegram Bot API and process messages
    while True:
        updates = get_updates()
        for update in updates:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            if chat_id == ALLOWED_CHAT_ID:
                # Process the message
                print(f"Received message from chat ID {chat_id}: {text}")
                if text.startswith('SET EMAIL'):
                    global MAIN_EMAIL
                    MAIN_EMAIL = text.split('SET EMAIL ')[1]
                    send_message(chat_id, f"Main email set to: {MAIN_EMAIL}")
                
                elif text.startswith('ADD DOMAIN'):
                    # global DOMAINS
                    domain = text.split('ADD DOMAIN ')[1]
                    if domain in DOMAINS:
                        send_message(chat_id, f"Domain already exists: {domain}")
                        return
                    current_time = int(time.time())
                    gen_email = hashlib.sha256(MAIN_EMAIL.encode() + domain.encode() + SECRET_HASH.encode() + str(current_time).encode())
                    DOMAINS[domain] = current_time
                    send_message(chat_id, f"0x{gen_email.hexdigest()}")

                elif text.startswith('REMOVE DOMAIN'):
                  # global DOMAINS
                  domain = text.split('REMOVE DOMAIN ')[1]
                  if domain not in DOMAINS:
                      send_message(chat_id, f"Domain does not exist: {domain}")
                      return
                  del DOMAINS[domain]

        # Add a delay before checking for updates again
        time.sleep(1)

if __name__ == '__main__':
    main()

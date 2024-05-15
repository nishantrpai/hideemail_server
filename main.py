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
SEND_MESSAGE_URL = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage'

# Define the URL for receiving updates from the Telegram Bot API
GET_UPDATES_URL = f'https://api.telegram.org/bot{TG_TOKEN}/getUpdates'

# Define the allowed chat ID
ALLOWED_CHAT_ID = MY_ID

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
    print("Getting updates...", f'https://api.telegram.org/bot{TG_TOKEN}/getUpdates')
    response = requests.get(f'https://api.telegram.org/bot{TG_TOKEN}/getUpdates')
    data = response.json()
    print(data)
    return data['result']

class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data,mail_options=None,rcpt_options=None):
        print(f"Received message from: {mailfrom}")
        print(f"Message recipients: {rcpttos}")
        print("Message data:")
        print(data)
        print("\n")

def main():
    # Generate a large random prime number
    bit_length = 1024
    prime_number = generate_large_random_prime(bit_length)
    print(prime_number)

    # Get current epoch time
    current_time = int(time.time())
    print(current_time)

    # Make a hash of the prime number and current epoch time
    hash_object = hashlib.sha256(str(prime_number).encode() + str(current_time).encode())
    print(hash_object.hexdigest())

    # Example email and domain
    email ='test@test.com'
    domain ='apple.com'
    gen_email = hashlib.sha256(email.encode() + domain.encode() + hash_object.hexdigest().encode())
    print('0x' + gen_email.hexdigest())

    # Start the SMTP server
    smtp_server = CustomSMTPServer(('0.0.0.0', 25), None)
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

        # Add a delay before checking for updates again
        time.sleep(1)

if __name__ == '__main__':
    main()

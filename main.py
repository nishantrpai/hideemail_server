import os
from telegram import ForceReply, Update
from telegram.ext import Application, filters, MessageHandler
from telegram import Bot

# people will configure their telegram bot token here
TG_TOKEN = os.getenv("TG_TOKEN")
MY_ID = os.getenv("MY_ID")


# when they deploy a large random prime number will be generated
import random
from sympy import isprime

domains = []

def generate_large_random_prime(bit_length):
    """
    Generate a large random prime number with the specified bit length.
    
    Parameters:
        bit_length (int): The desired bit length of the prime number.
        
    Returns:
        int: A large random prime number.
    """
    while True:
        # Generate a random number of the specified bit length
        n = random.getrandbits(bit_length)
        
        # Ensure that the number is odd and has the desired bit length
        n |= (1 << bit_length - 1) | 1
        
        # Check if the number is prime
        if isprime(n):
            return n

# Example usage:
bit_length = 1024  # Specify the desired bit length
prime_number = generate_large_random_prime(bit_length)
print(prime_number, '\n')

# get current epoch time
import time
current_time = int(time.time())
print(current_time)

# make a hash of the prime number and current epoch time
import hashlib
hash_object = hashlib.sha256(str(prime_number).encode() + str(current_time).encode())
print(hash_object.hexdigest())
# this hash will be used to encrypt the email based on the domain we want to share

email ='test@test.com'
domain ='apple.com'
gen_email = hashlib.sha256(email.encode() + domain.encode() + hash_object.hexdigest().encode())

# for this domain this is the encrypted email
print('0x' + gen_email.hexdigest())

# RUN YOUR SMTP SERVER
import smtpd
import asyncore

class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data,mail_options=None,rcpt_options=None):
        print(f"Received message from: {mailfrom}")
        print(f"Message recipients: {rcpttos}")
        print("Message data:")
        print(data)
        print("\n")



# when the telegram bot receives message we need to generate dynamic email
# based on the domain

def start(update, context):
    update.message.reply_text('Hello! I am your Telegram bot.')

# Define a function to handle incoming messages
def echo(update, context):
    # Check if the chat ID matches the allowed chat ID
    if update.message.chat_id == ALLOWED_CHAT_ID:
        update.message.reply_text(update.message.text)

def main():
    # Replace '0.0.0.0' with the IP address or hostname of your server
    # Replace 25 with the port number you want to use for SMTP

    # Initialize the Telegram bot
    print("Starting the Telegram bot...")
    
    application = Application.builder().token(TG_TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

    smtp_server = CustomSMTPServer(('0.0.0.0', 25), None)

    print("SMTP server started...")

    # Run the server indefinitely
    asyncore.loop()

if __name__ == '__main__':
    main()

# README.md

Mail server to generate one way email addresses

![dynamic email](https://imgur.com/oMxaOwf.png)

# Problem

When you sign up to a service say apple.com you join their email list.

Now they can sell this email to any provider and you will start getting spam.

# Solution

Use a one way email address.

When you sign up to apple.com you give them an email address that only works if they are the sender.

If anyone else tries to send an email to that address it will be rejected.

# Setup

1. Get a telegram bot token from @BotFather
2. Set the TG_TOKEN in the environment variable
3. Set MY_ID from the @userinfobot
4. Run the server
5. Set your email address SET EMAIL test@test.com
6. For each domain you can generate a new email ADD DOMAIN test.com (like the screenshot)

Deploy the server on a VPS and you can generate one way email addresses for any domain.

# Disclaimer

This is experimental software and should not be used for anything important.
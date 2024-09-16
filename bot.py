import os
import re
import requests
from faker import Faker
import random
import pycountry
import time

# Load environment variables
owner_id = os.getenv("OWNER_ID", "123456789")
owner_username = os.getenv("OWNER_USERNAME", "BotOwner")
bot_token = os.getenv("BOT_TOKEN")

faker = Faker()

def get_country_flag(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        code = country.alpha_2
        return ''.join([chr(127397 + ord(c)) for c in code])
    except LookupError:
        return "🏳️"

def clean(message):
    return message.strip()

def luhn_check(bin_number):
    sum_digits = 0
    num_digits = len(bin_number)
    odd_even = num_digits & 1

    for i in range(num_digits):
        digit = int(bin_number[i])
        if (i & 1) ^ odd_even:
            digit = digit * 2
            if digit > 9:
                digit -= 9
        sum_digits += digit

    return (sum_digits % 10) == 0

def get_bin_details(bin_number):
    url = 'http://bins.su/'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }
    data = {
        'action': 'searchbins',
        'bins': bin_number,
        'bank': '',
        'country': ''
    }

    response = requests.post(url, headers=headers, data=data)

    try:
        bank = clean(re.search(r'<td>Bank</td></tr><tr><td>(.*?)</td>', response.text).group(1))
        country = clean(re.search(fr'<td>{bank}</td><td>(.*?)</td>', response.text).group(1))
        brand = clean(re.search(fr'<td>{country}</td><td>(.*?)</td>', response.text).group(1))
        level = clean(re.search(fr'<td>{brand}</td><td>(.*?)</td>', response.text).group(1))
        card_type = clean(re.search(fr'<td>{level}</td><td>(.*?)</td>', response.text).group(1))
        return {
            'bin': bin_number,
            'bank': bank,
            'country': country,
            'brand': brand,
            'level': level,
            'type': card_type,
            'flag': get_country_flag(country)
        }
    except AttributeError:
        return None

def generate_fake_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def ipgen(amount=10):
    return [generate_fake_ip() for _ in range(amount)]

def generate_fake_details():
    country_name = faker.country()
    return {
        "name": faker.name(),
        "address": faker.address(),
        "country": f"{country_name} {get_country_flag(country_name)}",
        "zip_code": faker.zipcode(),
        "email": faker.email(),
        "phone_number": faker.phone_number(),
        "account_number": faker.bban(),
        "bank": faker.bank(),
        "routing_number": faker.aba()
    }

def show_credits():
    return f"🤖 *Bot created by {owner_username}* (ID: {owner_id})\n🌟 Powered by Python and the Faker library."

def handle_command(command, user_id, params=None):
    if command == "/start":
        return f"👋 Welcome to the bot!\nUse /help to see available commands."

    elif command == "/help":
        return """
🤖 *Bot Commands*:
- /start: Welcome message
- /ping: Check if the bot is online
- /ipgen: Generate fake IP addresses
- /faker: Generate fake details
- /bin: Get details from BIN (e.g., /bin 123456)
- /credits: Show bot and owner information
- /admin: Admin-only commands (owner)
- /shutdown: Shut down the bot (admin only)
- /status: Check bot status (admin only)
        """

    elif command == "/credits":
        return show_credits()

    elif command == "/ping":
        return "🏓 Pong! The bot is online and ready!"

    elif command == "/ipgen":
        return f"🖥️ Here are some randomly generated IP addresses:\n{ipgen()}"

    elif command == "/faker":
        fake_details = generate_fake_details()
        return f"📝 Fake Details:\nName: {fake_details['name']}\nAddress: {fake_details['address']}\nCountry: {fake_details['country']}\nEmail: {fake_details['email']}\nPhone: {fake_details['phone_number']}"

    elif command == "/bin" and params:
        bin_number = params[0][:6]
        if not luhn_check(bin_number):
            return "❌ Invalid BIN (failed Luhn check)."

        bin_details = get_bin_details(bin_number)
        if bin_details:
            return f"💳 BIN Details:\nBank: {bin_details['bank']}\nCountry: {bin_details['country']} {bin_details['flag']}\nBrand: {bin_details['brand']}\nLevel: {bin_details['level']}\nType: {bin_details['type']}"
        else:
            return "⚠️ BIN details not found."

    elif command == "/admin":
        if str(user_id) == owner_id:
            return f"👑 *Welcome, {owner_username}* (ID: {owner_id})!\nHere are your admin commands:\n- /shutdown: Shut down the bot\n- /status: Check bot status"
        else:
            return "🚫 You are not authorized to use admin commands."

    elif command == "/shutdown" and str(user_id) == owner_id:
        return "⚠️ Bot is shutting down..."

    elif command == "/status" and str(user_id) == owner_id:
        return "✅ Bot is up and running!"

    else:
        return "⚠️ Command not recognized. Use /help to see available commands."

def main_loop():
    while True:
        # Here, you would implement the logic to periodically check for new commands,
        # handle incoming requests, etc. For simplicity, we'll just sleep.
        # In a real-world scenario, you might use a task queue or similar to handle work.
        print("Bot is running...")
        time.sleep(60)  # Sleep for 60 seconds

if __name__ == "__main__":
    main_loop()

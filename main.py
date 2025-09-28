import requests
import smtplib
from email.mime.text import MIMEText
import os
import sys

# Get environment variables from GitHub Secrets
BTC_ADDRESS = os.getenv('BTC_ADDRESS')
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # App password for Gmail
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

if not all([BTC_ADDRESS, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
    print("Missing required environment variables.")
    sys.exit(1)

def get_btc_balance(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        balance_satoshis = data.get('final_balance', 0)
        return balance_satoshis / 100_000_000  # Convert satoshis to BTC
    else:
        raise Exception(f"Failed to fetch balance: {response.status_code} - {response.text}")

def get_btc_usd_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['bitcoin']['usd']
    else:
        raise Exception(f"Failed to fetch BTC price: {response.status_code} - {response.text}")

def send_email(balance_btc, balance_usd):
    subject = f"BTC Balance Update for {BTC_ADDRESS}"
    body = f"Current balance: {balance_btc:.8f} BTC\nValue in USD: ${balance_usd:,.2f}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        balance_btc = get_btc_balance(BTC_ADDRESS)
        btc_price_usd = get_btc_usd_price()
        balance_usd = balance_btc * btc_price_usd
        send_email(balance_btc, balance_usd)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
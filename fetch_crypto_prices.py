import time
import csv
import requests

# Define the cryptocurrency symbol and CSV file path
crypto_symbol = 'bitcoin'
csv_file_path = 'crypto_prices.csv'

# Function to fetch cryptocurrency price
def fetch_crypto_price(symbol):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[symbol]['usd']
    else:
        raise Exception(f'Error fetching price: {response.status_code}')

# Function to log price in CSV
def log_price(price):
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), price])

# Main loop to periodically fetch and log the price
if __name__ == '__main__':
    while True:
        try:
            price = fetch_crypto_price(crypto_symbol)
            log_price(price)
            print(f'Logged price: {price}')
        except Exception as e:
            print(f'An error occurred: {e}')
            time.sleep(60)  # Wait before retrying
        time.sleep(60)  # Wait before the next fetch
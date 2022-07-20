
import pandas
import requests
import csv
import time 
import json
# Token name
token_symbol = "BNB"
# URL to get the coin_id 
url_coin = 'https://www.coingecko.com/en/coins/'
# URL to scrape the coin_price 
url_price = 'https://www.coingecko.com/price_charts/'
# URL to scrape the coin_market_cap
url_market_cap = 'https://www.coingecko.com/market_cap/'

# Get a coin id in coingecko backend
# # Arguments
# * 'coin_name' - The coin's name
def get_coin_id(coin_name):
    coin_data = requests.get(url_coin + coin_name)
    index = coin_data.text.find('id="coin_id" value=')
    sub_str = coin_data.text[index + 19: index + 19 + 10].split('"')
    coin_id = 0
    for x in sub_str:
        if(x.isdigit()):
            coin_id = x
    return coin_id
# Scrape the daily data from 1y chart and save it in coingecko.csv file
# # Arguments
# * 'coin_name' - The coin's name
def coingecko_scrapper_1y(token_name):
    # get coin id
    coin_id = get_coin_id(token_name.lower())
    # scrape price data from coingecko backend
    price_data = requests.get(url_price + coin_id + "/usd/365_days.json").json()
    # scrape marketCap data from coingecko backend
    market_data = requests.get(url_market_cap + coin_id + "/usd/365_days.json").json()
    
    timestamp_csv = ["TimeStamp"]
    price_csv = ["Price"]
    market_cap_csv = ["MarketCap"]
    total_volumes_csv = ["TotalVolumes"]
    for i in range(0, len(price_data["stats"]) - 1, 1):
        timestamp_csv.append(price_data["stats"][i][0])
        price_csv.append(price_data["stats"][i][1])
        market_cap_csv.append(market_data["stats"][i][1])
        total_volumes_csv.append(price_data["total_volumes"][i][1])
    # open therfile in the write mode
    f = open('./coingecko.csv', 'w')
    # create ther csv writer
    writer = csv.writer(f)
    # writer a row to ther csv file
    writer.writerow(timestamp_csv)
    writer.writerow(price_csv)
    writer.writerow(market_cap_csv)
    writer.writerow(total_volumes_csv)
    # close the file 
    f.close()

# Run the scrapper
coingecko_scrapper_1y(token_symbol)
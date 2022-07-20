
import pandas
import requests
import csv
import time 
import json

# Token name
token_name = 'quick-stmatic-matic'
# Period segment
period = 'day'
# Amount of sample data witch we are going to scrape
limit_num = 395
# Second per day
seconds_per_day = 86400

# Scrape the daily data from 1y chart and save it in beefy.csv file
# # Arguments
# * 'coin_name' - The coin's name
def beefy_scrapper_1y(coin_name):
    # Current time
    to_sec = round(time.time())
    # 
    from_sec = to_sec - limit_num * seconds_per_day
    # Olympus Pro subgraph url which trading stuff data is recorded
    url_price = 'https://data.beefy.finance/price'
    url_apy = 'https://data.beefy.finance/apy'
    params = {
        'name': coin_name,
        'period': period,
        'from': from_sec,
        'to': to_sec,
        'limit': limit_num
    }
    # Sample query data
    array_price = requests.get(url_price, params = params).json()
    array_apy = requests.get(url_apy, params = params).json()
    # open therfile in the write mode
    f = open('./beefy.csv', 'w')

    # create ther csv writer
    writer = csv.writer(f)
    timestamp_csv = ["TimeStamp"]
    price_csv = ["Price"]
    apy_csv = ["APY"]
    for x in range(0, len(array_price) - 1, 1):
        timestamp_csv.append(array_price[x]["ts"])
        price_csv.append(array_price[x]["v"])
        apy_csv.append(array_apy[x]["v"])

    # writer a row to ther csv file
    writer.writerow(timestamp_csv)
    writer.writerow(price_csv)
    writer.writerow(apy_csv)
    # close the file 
    f.close()

# Run the scrapper
beefy_scrapper_1y(token_name)


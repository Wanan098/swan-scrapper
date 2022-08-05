
from urllib import response
import pandas
import csv
from web3 import Web3
from datetime import datetime
import json
from requests import get

MORALIS_API_KEY = 'blknTmGyJhd6w9cLtAQf1qMY1281XZumz2iRQQf0dJPw4qfGtxv6WQttmplz1rBe'
BASE_URL = "https://deep-index.moralis.io/api/v2/"
CHAIN = "eth"
INPUT_CSV_PATH = './input.csv'
OUTPUT_CSV_PATH = './output.csv'

# csv reader for specific file path
def csv_reader(path):
    f = open(path, 'r')

    reader = csv.reader(f, delimiter=',')
    row_array = []
    for row in reader:
        row_array.append(row)
    return row_array

# csv append writer for specific file path
def csv_writer(path, elems):
    with open(path, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        for x in elems:
            csv_writer.writerow(x)

# create token transfer api call url function
def make_token_transfer_api_url(address, chain, block_number):
    url = BASE_URL + f"{address}/erc20/transfers?chain={chain}&from_block={int(block_number)}&to_block={int(block_number)}"
    return url
# create transaction api call url function
def make_get_transaction_api_url(tx_hash, chain):
    url = BASE_URL + f"transaction/{tx_hash}?chain={chain}"
    return url
# create token metadata api call url function
def make_get_token_metadata_api_url(addresses, chain):
    url = BASE_URL + f"erc20/metadata?chain={chain}"
    for x in addresses:
        url += f"&addresses={x}"
    return url
# create token price api call url function
def make_get_token_price_api_url(address, chain, to_block):
    url = BASE_URL + f"erc20/{address}/price?chain={chain}&to_block={to_block}"
    return url

# create token price api call url function
def make_day_to_block_api_url(time, chain):
    url = BASE_URL + f"dateToBlock?chain={chain}&date={time}"
    return url

def get_token_transfer_data(address, chain, block_number):
    token_transfer_url = make_token_transfer_api_url(address, chain, block_number)
    response = get(token_transfer_url, headers={"accept": "application/json", "X-API-Key": MORALIS_API_KEY})
    data = response.json()
    transfer_data = []
    addresses = []
    for tx_data in data['result']:
        if addresses.count(tx_data['address']) == 0:
            addresses.append(tx_data['address'])
            transfer_data.append({
                tx_data['address']: tx_data['address'],
                'value': tx_data['value']
            })
    return (transfer_data, addresses)
def get_token_metadata(token_addresses, chain):
    token_metadata_url = make_get_token_metadata_api_url(token_addresses, chain)
    response = get(token_metadata_url, headers={"accept": "application/json", "X-API-Key": MORALIS_API_KEY})
    data = response.json()
    token_metadata = []
    for x in data:
        token_metadata.append({
            x['address']: x['address'],
            'symbol': x['symbol'],
            'decimals': x['decimals']
        })
    return token_metadata
def get_token_price(token_addresses, block_number, chain):
    price_array = []
    for x in token_addresses:
        token_price_url = make_get_token_price_api_url(x, chain, block_number)
        response = get(token_price_url, headers={"accept": "application/json", "X-API-Key": MORALIS_API_KEY}).json()
        price_array.append(
            response['usdPrice'],
        )
    return price_array
def get_passed_block_number(original_timestamp, day, chain):
    original_dt_obj = datetime.strptime(original_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    original_millisec = original_dt_obj.timestamp()
    measured_time = original_millisec + 86400 * int(day)
    day_to_block_url = make_day_to_block_api_url(measured_time, chain)
    response = get(day_to_block_url, headers={"accept": "application/json", "X-API-Key": MORALIS_API_KEY})
    block_number = response.json()['block']
    return block_number
def get_transaction(tx_hash, passed_day, chain):
    transaction_url = make_get_transaction_api_url(tx_hash, chain)
    response = get(transaction_url, headers={"accept": "application/json", "X-API-Key": MORALIS_API_KEY})
    data = response.json()
    token_transfer_data, token_addresses = get_token_transfer_data(data["to_address"], chain, data["block_number"])    
    token_metadata = get_token_metadata(token_addresses, chain)

    token_price_transacted_time = get_token_price(token_addresses, data['block_number'], chain)
    token_price_passed_days = get_token_price(token_addresses, get_passed_block_number(data['block_timestamp'], passed_day, chain), chain)
    scraping_result = []
    for x in range(len(token_addresses)):
        amount_with_decimals = int(token_transfer_data[x]['value']) / pow(10, int(token_metadata[x]['decimals']))
        scraping_result.append({
            'token_name': token_metadata[len(token_addresses) - x - 1]['symbol'],
            'amount': amount_with_decimals,
            'before_price': token_price_transacted_time[x],
            'after_price': token_price_passed_days[x],
            'before_value': token_price_transacted_time[x] * amount_with_decimals,
            'after_value': token_price_passed_days[x] * amount_with_decimals
        })
    print(scraping_result)
    return scraping_result
transaction_input_data = csv_reader(INPUT_CSV_PATH)
for x in transaction_input_data:
    result = get_transaction(x[0], x[1], CHAIN)
    tx_hash = ["Transaction Hash", x[0]]
    token_name = ['Token Name']
    amount = ['Amount']
    before_price = ['Price Before']
    after_price = ['Price After']
    before_value = ['Value Before']
    after_value = ['Value After']
    for x in range(len(result)): 
        token_name.append(result[x]['token_name'])
        amount.append(result[x]['amount'])
        before_price.append(result[x]['before_price'])
        after_price.append(result[x]['after_price'])
        before_value.append(result[x]['before_value'])
        after_value.append(result[x]['after_value'])
    csv_result = [
        [],
        tx_hash,
        token_name,
        amount,
        before_price,
        before_value,
        after_price,
        after_value
    ]
    csv_writer('./output.csv', csv_result)

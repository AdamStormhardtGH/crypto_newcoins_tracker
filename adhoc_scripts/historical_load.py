"""
will get all historic data for all coins as a single jsonld
uses coingecko api

standalone script

"""

from pycoingecko import CoinGeckoAPI
from requests.models import HTTPError
import json, time, os, arrow, datetime
import boto3

def get_coins_details(coin_id ):
    """
    endpoint for getting data for coins details
    pulled out into its own component so we can easily replace 
    end_date is required. this allows us to cap the report in days
    """
    print(f"getting coin details for: {coin_id}")
    cg = CoinGeckoAPI()

    max_retries = 10
    retry_number = 0
    wait = 61
    success = False
    time.sleep(1.1)
    while success == False and retry_number < max_retries:
        try:
            coin_details = cg.get_coin_market_chart_by_id(id=coin_id,vs_currency="aud", days="max", interval="daily")  #get the 24 hour 
            success = True
        except HTTPError as e:
            if e.response.status_code == 429:
                retry_number = retry_number + 1
                print(f"too many requests error. Waiting {wait} seconds")
                time.sleep(wait) #wait for this to ease up by waiting for a minute
            else:
                break
        

    historic_coin_details_list = extract_historical_market_value_for_coins(coin_details,coin_id=coin_id)

    return historic_coin_details_list


def extract_historical_market_value_for_coins(coin_details,coin_id,days):

    print("extract_historical_market_value_for_coins()")
    end_entry = -1 #the entry which isn't the time at the call - looks like range uses the last item the same as a < symbol. 
    coins_to_get_startingpoint = 0
    coin_history = []

    #apply the indexing based on start and end
    coin_index = []
    
    print(coin_details["prices"][coins_to_get_startingpoint:end_entry])
    for eachindex in coin_details["prices"][coins_to_get_startingpoint:end_entry]:
        coin_index.append(coin_details["prices"].index(eachindex))

    age = 0
    for each_entry in coin_index:
        coin_data = {
            "id": coin_id,
            "date": epoch_to_timestamp(coin_details["prices"][each_entry][0]), #was -1 for latest. lets just get the minight volume
            "prices": coin_details["prices"][each_entry][-1],
            "market_caps": coin_details["market_caps"][each_entry][-1],
            "total_volumes": coin_details["total_volumes"][each_entry][-1],
            "age": age
        }
        age = age + 1
        coin_history.append(coin_data)
    
    return coin_history


def epoch_to_timestamp(epoch_string):
    """
    converts data from epoch to athena friendly timestamp
    """
    
    epoch_string_clean = str(int(epoch_string/1000) ) #remove milliseconds
    try:
        formatted_timestamp = arrow.get(epoch_string_clean,"X").format("YYYY-MM-DD HH:mm:ss")
    except:
        formatted_timestamp = datetime_now().format("YYYY-MM-DD HH:mm:ss")
    return formatted_timestamp

def get_coins_list():
    """
    endpoint for getting data for coins list
    pulled out into its own component so we can easily replace 
    """
    cg = CoinGeckoAPI()
    return cg.get_coins_list()

def orchestrate_historic_data_extraction():

    coin_list = get_coins_list()

    historic_data = []
    for each_coin in coin_list:
        try:
            coin_id = each_coin["id"]
            historic_data.extend(get_coins_details(coin_id=coin_id))
        except:
            pass
    
    ldjson = list_of_dicts_to_jsonl(historic_data)

    BUCKET = os.getenv('BUCKET')
    COINS_PATH = os.getenv('COINS_PATH')
    path = f"{COINS_PATH}/historic_load.json"

    write_file(input_string_data=ldjson,filepath="./historic_data.json")
    write_to_storage(data=ldjson,bucket=BUCKET,filename_path=path)

def list_of_dicts_to_jsonl(list_input):
    """
    takes a list of dict objects and turns it into a jsonl doc
    """

    jsonl_contents = ""
    for each_entry in list_input:
        jsonl_contents = jsonl_contents + "\n" + json.dumps(each_entry)
    
    return jsonl_contents

def write_file(input_string_data,filepath):
    """ 
    write a file with data
    """

    with open(filepath,"w") as new_file:
        new_file.write(input_string_data)

def datetime_now():
    """
    returns UTC now time
    add .format('YYYY-MM-DD HH:mm:ss ZZ') to convert to ISO
    add .format()
    """
    return arrow.utcnow()

# write_file(input_string_data="hello",filepath="./hello.json")

def write_to_storage(data, bucket, filename_path):
    """"
    will write data to a storage location
    """
    print("performing putObject")
    client = boto3.client('s3')
    return client.put_object(Body=data, Bucket=bucket, Key=filename_path)

orchestrate_historic_data_extraction()
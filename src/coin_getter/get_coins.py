"""
will pull details for a specific coin from an API (coingecko)
and write to s3 based on environment variables
"""
from pycoingecko import CoinGeckoAPI
import utils
import os
from dotenv import load_dotenv
load_dotenv()


def orchestrate_coin_getter(coin_id, days="max"):
    """
    orchestrate the getter of coins. 
    Deal with single and multiple days
    """
    print(f"coin_id: {coin_id}")
    try: 
        BUCKET = os.getenv('BUCKET')
        COIN_MARKET_DATA_PATH = os.getenv('COIN_MARKET_DATA_PATH')
    except Exception as e:
        print(f"error initializing coin getter environments: {e}")

    
    coin_data_raw = get_coin(coin_id=coin_id, days=days)
    coin_path_latestdate = coin_data_raw[-1]["date"]
    date_partition = utils.partition_path_from_date(coin_path_latestdate)
    coin_path = f"{COIN_MARKET_DATA_PATH}/{date_partition}/{coin_path_latestdate}_{coin_id}.json"
    coin_data_jsonl = utils.list_of_dicts_to_jsonl(coin_data_raw)
    s3write_status = utils.write_to_storage(data=coin_data_jsonl, bucket=BUCKET,filename_path=coin_path)
    return s3write_status
    

def get_coin(coin_id,days=1):
    """
    get the coin from the api
    defaults to single day
    days option 1,2, 3, 30, max
    returns list of items
    """
    print(f"getting coin details for: {coin_id}")
    if days == 'max':
        pass
    else:
        days = int(days)
    cg = CoinGeckoAPI()
    coin_details = cg.get_coin_market_chart_by_id(id=coin_id,vs_currency="aud", days=days, interval="daily")  #get the 24 hour 
    print(coin_details)
    latest_coin_details = extract_historical_market_value_for_coins(coin_details,coin_id=coin_id,days=days)

    return latest_coin_details


def extract_historical_market_value_for_coins(coin_details,coin_id,days):

    
    end_entry = -1 #the entry which isn't the time at the call - looks like range uses the last item the same as a < symbol. 
    # if days == 'max':
    #     coins_to_get_startingpoint = 0
    # else: 
    #     coins_to_get_startingpoint = end_entry-days
    coins_to_get_startingpoint = 0
    coin_history = []

    #apply the indexing based on start and end
    coin_index = []
    print(coin_details["prices"][coins_to_get_startingpoint:end_entry])
    for eachindex in coin_details["prices"][coins_to_get_startingpoint:end_entry]:
        print(eachindex)
        coin_index.append(coin_details["prices"].index(eachindex))

    for each_entry in coin_index:
        coin_data = {
            "id": coin_id,
            "date": utils.epoch_to_timestamp(coin_details["prices"][each_entry][0]), #was -1 for latest. lets just get the minight volume
            "prices": coin_details["prices"][each_entry][-1],
            "market_caps": coin_details["market_caps"][each_entry][-1],
            "total_volumes": coin_details["total_volumes"][each_entry][-1]
            # "age": len(coin_details["total_volumes"])-2
        }
        coin_history.append(coin_data)
    
    return coin_history



# print(get_coin("shibgf","1"))
# print(orchestrate_coin_getter("shiba","max") )
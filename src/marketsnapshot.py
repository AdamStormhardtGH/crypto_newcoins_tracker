"""
Will get a list of all coins in the market at the moment
"""
from pycoingecko import CoinGeckoAPI
import utils


def get_market_snapshot():
    """
    will call an api to get the market snapshot, returning json with a timestamp
    """
    date_now = utils.datetime_now()
    market_snapshot = {"date": date_now.format('YYYY-MM-DD HH:mm:ss')}
    market_snapshot["data"] = get_coins_list()

    year = date_now.year
    month = date_now.month
    day = date_now.day

    storagebucket = "coin-analysis-data-ar-staging"
    path = f"snapshots/year={year}/month={month}/day={day}/snapshot.json"
    data = utils.dict_to_jsonl(market_snapshot)

    status = utils.write_to_storage(data=data, bucket=storagebucket, filename_path=path)
    return status

def get_coins_list():
    """
    endpoint for getting data for coins list
    pulled out into its own component so we can easily replace 
    """
    cg = CoinGeckoAPI()
    return cg.get_coins_list()

print(get_market_snapshot())


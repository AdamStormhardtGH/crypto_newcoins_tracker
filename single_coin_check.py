"""
test the get and write of a single coin
"""

from src import getwatchlistdetails
from src.coin_getter import utils as cgutils
from src.coin_getter import get_coins as cg_getcoins
import os


BUCKET = os.getenv('BUCKET')
# athena and s3
getwatchlistdetails.get_watch_list()

# s3 read
# s3 write
coin_data_raw = cg_getcoins.get_coin(coin_id="bitcoin", days=1) #this is a list
coin_data_jsonl = cgutils.list_of_dicts_to_jsonl(coin_data_raw)
s3write_status = cgutils.write_to_storage(data=coin_data_jsonl, bucket=BUCKET,filename_path="testdata/testdata-btc.json")

print("testing success")
"""
compares yesterday's markets with today. Creates a series of coins to listen to based in the delta
"""
import arrow
import utils
import os 
from dotenv import load_dotenv
import json

load_dotenv()



def read_snapshot_from_date(supplied_date):
    """
    loads the snapshot from s3 based on current date
    expects an arrow datetime object, but if it doesn't exist it'll pull today's date from datetime
    """
    BUCKET = os.getenv('BUCKET')
    SNAPSHOT_PATH = os.getenv('SNAPSHOT_PATH')
    SNAPSHOT_FILENAME = os.getenv('SNAPSHOT_FILENAME')
    
    year = supplied_date.year
    month = supplied_date.month
    day = supplied_date.day

    snapshot_path = f"{SNAPSHOT_PATH}/year={year}/month={month}/day={day}/{SNAPSHOT_FILENAME}"

    s3_file = utils.read_from_storage(bucket = BUCKET, filename_path=snapshot_path)
    s3_file_data = json.loads(s3_file['Body'].read())
    
    return s3_file_data



def compare_yesterday_and_today():
    """
    orchestrates the comparison of date between dates
    returns the delta as a list with the watchlist snapshot date in each object within
    results will end up int he watchlist path within the specified bucket
    """

    today = utils.datetime_now()
    yesterday = utils.datetime_now().shift(days=-1)

    today_data = read_snapshot_from_date(today)
    yesterday_data = read_snapshot_from_date(yesterday)
    delta  = []

    #iterate through all coins in list and look for new ones
    for each_coin in today_data["data"]:
        match = False
        for each_coin_yesterday in yesterday_data["data"]:
            if each_coin["id"] == each_coin_yesterday["id"]:
                match = True
        if match == False:
            each_coin["added_date"] = today_data["date"]
            delta.append(each_coin)

    if len(delta) > 0:
        print(f"found coins: {delta}")
        status = write_delta_to_watch_location(delta_list=delta, date_value=today)
        return status
    else:
        return "No new coins today"


def write_delta_to_watch_location(delta_list,date_value):
    """
    will take a list (ideally with the deltas from 2 dates) and will write to watch location (s3)
    """

    BUCKET = os.getenv('BUCKET')
    SNAPSHOT_PATH = os.getenv('WATCHLIST_PATH')
    SNAPSHOT_FILENAME = f"{os.getenv('WATCHLIST_FILENAME')}"

    year = date_value.year
    month = date_value.month
    day = date_value.day

    path = f"{SNAPSHOT_PATH}/year={year}/month={month}/day={day}/{SNAPSHOT_FILENAME}"

    delta_jsonl = utils.list_of_dicts_to_jsonl(delta_list)
    status = utils.write_to_storage(data=delta_jsonl, bucket=BUCKET, filename_path=path)

    return status

print( compare_yesterday_and_today() )

"""
check prices for all coins daily, then compress it and upload the single file to s3
"""

from src import getwatchlistdetails
from src import utils
from src import marketsnapshot
import time
from pathlib import Path
import os
import arrow
import gzip

from dotenv import load_dotenv
load_dotenv()

def join_multiple_data_files_ldjson(input_folder_path,output_path,file_prefix=None):
    """
    
    """
    import re
    consolidated_dataset = []
    
    output_full_path = f"{output_path}/{file_prefix}_daily_data.json"

    import os
    import glob
    try:
        list_of_files = (glob.glob(f"{input_folder_path}/**")) 
        print(len(list_of_files))
        for each in list_of_files:
            with open(each,"r") as jsf:
                coin_data = jsf.read()
            coin_data = re.sub(r"^$\n","",coin_data)
            consolidated_dataset.append(coin_data)
        
        output_string = ''.join(consolidated_dataset)
        with open(output_full_path,"w") as hist_file:
            hist_file.write(output_string)
        return output_full_path
    except:
        return ""


def orchestrate_daily_coin_check():
    """
    main function to do the dance of getting all coins from the list,
    then downloading them to a temp file based on the date
    then concatinating all files inside the dir them with a simple loop script
    then compressing them with gz
    then uploading them to s3
    """

    BUCKET = os.getenv('BUCKET')
    ALL_COINS_PATH = os.getenv('ALL_COINS_PATH')
    
    coins_list = marketsnapshot.get_coins_list()

    # coins_list = [{"id":"cointribe"},{"id":"exodia-inu"}, {"id":"gameology"}, {"id":"gameologyv2"}, {"id":"gameonetoken"}, {"id":"gamercoin"} ]

    day = utils.datetime_now().shift(days=-1).format("YYYY-MM-DD")
    date_year = arrow.get(day).format("YYYY")
    date_month = arrow.get(day).format("MM")
    date_day = arrow.get(day).format("DD")

    temp_write_path = f"~/temp/{day}/splitcoins"
    temp_concatinated_file_path = f"~/temp/{day}"
    Path(temp_write_path).mkdir(parents=True, exist_ok=True)
    Path(temp_concatinated_file_path).mkdir(parents=True, exist_ok=True)

    coins_list_ids = []
    for each_item in coins_list:
        if len(each_item["id"]) >0:
            coins_list_ids.append(each_item["id"])

    #now lets process the coins
    for each_coin in coins_list_ids:
        time.sleep(0.9)
        print(f"looking for {each_coin}")
        try: 
            latest_coin_details = getwatchlistdetails.get_coins_details(each_coin)
            
            if isinstance(latest_coin_details, list):
                ldjson = utils.list_of_dicts_to_jsonl(latest_coin_details)
            elif isinstance(latest_coin_details, dict):
                ldjson = utils.dict_to_jsonl(latest_coin_details)
            
            with open(f"{temp_write_path}/{each_coin}.json","w") as write_file:
                write_file.write(ldjson)
        except Exception as e:
            print(f"skipped coin {each_coin} due to errors - {e}")
    
    # utils.notify_discord_bot(f"daily coin check for all coins complete for {day}. compressing and writing to s3...")
    
    join_files_path = join_multiple_data_files_ldjson(input_folder_path=temp_write_path,output_path=temp_concatinated_file_path, file_prefix=day)
    gz_path = f"{join_files_path}.gz"
    
    #write to gz
    with open(join_files_path, 'rb') as orig_file:
        with gzip.open(gz_path, 'wb') as zipped_file:
            zipped_file.writelines(orig_file)

    s3_path_prefix = f"year={date_year}/month={date_month}/day={date_day}"
    full_path_to_write = f"{ALL_COINS_PATH}/{s3_path_prefix}/{day}_all_coin_data.json.gz"


    if join_files_path != None:
        #open the file 
        with open(gz_path, "rb") as concat_file:
            concat_contents = concat_file.read()
        outcome = utils.write_to_storage(data=concat_contents,bucket=BUCKET,filename_path=full_path_to_write )
        print(outcome)

    utils.notify_discord_bot(f"initial load complete - {outcome}")
        

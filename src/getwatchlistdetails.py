"""
Gets the watchlist and queries details for each coin in watchlist
Outputs details in partitioned watchlist report json
"""
from datetime import date
import json, os, time
import boto3
from pycoingecko import CoinGeckoAPI
from requests.models import HTTPError
from . import utils
# import utils

from dotenv import load_dotenv
load_dotenv()

def queue_coins_to_get(days=1):
    """
    will prepare list of coin ids we need and enqueue them
    """
    print("queue_coins_to_get()")
    watch_list = get_watch_list() #expects list
    cleaned_queue = []
    for each_coin in watch_list:
        if len(each_coin)>0:
            if each_coin not in cleaned_queue:
                cleaned_queue.append(each_coin)
                
    utils.batch_send_to_sqs(coin_list=cleaned_queue,days=days)
    print("coins enqueued")

def orchestrate_watchlist_details_check():
    """
    ** FOR EC2 ***
    *** MAIN ORCHESTRATOR FOR THIS FUNCTIONALITY ***
    orchestrate the querying and processing and storage of market data for coins on watchlist
    then store to s3
    """
    print("orchestrate_watchlist_details_check()")
    #query all coins on watchlist and get updated data based on query time (like now)
    watch_list = get_watch_list()
    market_coins = get_coins_data_from_market(watchlist=watch_list)


    BUCKET = os.getenv('BUCKET')
    COINS_PATH = os.getenv('COINS_PATH')
    COINS_FILENAME = os.getenv('COINS_FILENAME')

    date_value = utils.datetime_now()

    epoch = round(float(date_value.format("X")))
    year = date_value.year
    month = date_value.month
    day = date_value.day

    path = f"{COINS_PATH}/year={year}/month={month}/day={day}/{epoch}_{COINS_FILENAME}"

    market_coins_jsonl = utils.list_of_dicts_to_jsonl(market_coins)
    status = utils.write_to_storage(data=market_coins_jsonl, bucket=BUCKET, filename_path=path)

    return market_coins
    # f"Updated market details for {len(market_coins)} coins in watch list"


###all the components are below


def get_watch_list():
    """
    performs a query from athena to get the watch list
    """
    # today_date_epoch = utils.startofday_epohc_now
    
    

    ATHENA_WATCHLIST_TABLE = os.getenv('ATHENA_WATCHLIST_TABLE')
    ATHENA_DATABASE = os.getenv('ATHENA_DATABASE')

    query = f"""
        SELECT distinct id
        from {ATHENA_WATCHLIST_TABLE}
        where id != ''
        """ #change this to id for prod

    client = boto3.client('athena', region_name='us-east-1')
    athena_watch_list_query_id = client.start_query_execution(
        QueryString = query,
        
        QueryExecutionContext={
            'Database': ATHENA_DATABASE,
            'Catalog': 'AwsDataCatalog'
        },
        ResultConfiguration={
            'OutputLocation': 's3://athena-query-results-ar-staging/',
            # 'EncryptionConfiguration': {
            #     'EncryptionOption': 'SSE_S3'|'SSE_KMS'|'CSE_KMS'
            # }
        },
    )

    execution_id = athena_watch_list_query_id['QueryExecutionId']
    
    #check status of query
    status = 'QUEUED'
    while status == 'RUNNING' or status == 'QUEUED':
        time.sleep(1)
        status = client.get_query_execution(QueryExecutionId=execution_id)['QueryExecution']['Status']['State']
        print(status)
        # print(f"{status} : {execution_id} \n\n")

    if status == 'FAILED' or status == 'CANCELLED':
        print("query failed!")
        # exit(0)

    athena_watch_list_query_data = client.get_query_results(
        QueryExecutionId=execution_id,
        # NextToken='string',
        # MaxResults=123
    )

    #clean up this data
    watchlist = extract_values_from_query_response(athena_watch_list_query_data)
    return watchlist



def extract_values_from_query_response(input_payload=None):
    """
    takes query results data and returns a list
    """
    # mockdata = {'UpdateCount': 0, 'ResultSet': {'Rows': [{'Data': [{'VarCharValue': 'symbol'}]}, {'Data': [{'VarCharValue': 'pappay'}]}, {'Data': [{'VarCharValue': 'akira'}]}, {'Data': [{'VarCharValue': 'akita'}]}], 'ResultSetMetadata': {'ColumnInfo': [{'CatalogName': 'hive', 'SchemaName': '', 'TableName': '', 'Name': 'symbol', 'Label': 'symbol', 'Type': 'varchar', 'Precision': 2147483647, 'Scale': 0, 'Nullable': 'UNKNOWN', 'CaseSensitive': True}]}}, 'ResponseMetadata': {'RequestId': '540e0078-bd31-40e0-9e8e-07d81c1f7496', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Sun, 31 Oct 2021 02:57:15 GMT', 'x-amzn-requestid': '540e0078-bd31-40e0-9e8e-07d81c1f7496', 'content-length': '690', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
    # input_payload = mockdata

    coins = []

    rows = input_payload['ResultSet']['Rows']
    for each_row in rows:
        for each in each_row['Data']:
            for key, value in each.items():
                coins.append(value)
    del coins[0] #remove header
    return coins




def get_coins_data_from_market(watchlist):
    """
    
    given a list of items, query an endpoint and return the data into a list
    then store to s3
    """

    coins_with_details = []
    for each_coin in watchlist:
        time.sleep(1.1)
        print(f"looking for {each_coin}")
        try: 
            coins_with_details.append(get_coins_details(each_coin) )
        except:
            print(f"skipped coin {each_coin} due to errors")
    
    return coins_with_details


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
        

    latest_coin_details = extract_latest_market_value_for_coin(coin_details)
    latest_coin_details["id"] = coin_id #add id to help us joins

    return latest_coin_details

def extract_latest_market_value_for_coin(coin_details):
    """
    for coingecko, looks at market data and only gets the values with associated epoch 
    """
    try:
        latest_coin_data = {
            "date": utils.epoch_to_timestamp(coin_details["prices"][-2][0]), #was -1 for latest. lets just get the minight volume
            "prices": coin_details["prices"][-2][-1],
            "market_caps": coin_details["market_caps"][-2][-1],
            "total_volumes": coin_details["total_volumes"][-2][-1],
            "age": len(coin_details["total_volumes"])-2
        }
    except:
        latest_coin_data = {
            "date": utils.datetime_now().format("YYYY-MM-DD HH:mm:ss"),
            "prices": 0,
            "market_caps": 0,
            "total_volumes": 0,
            "age": 0
        }


    

    return latest_coin_data




# print(get_watch_list() )
# extract_values_from_query_response()

# print(get_coins_details('akira') )
# print(utils.startofday_epohc_now() )

# print(orchestrate_watchlist_details_check() )

# for each in range(0,100):
#     print(get_coins_details('akira'))
    



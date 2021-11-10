"""
Shared utilities
"""

import arrow, json, time
import re, os
import boto3
import requests
from dotenv import load_dotenv
load_dotenv()

def datetime_now():
    """
    returns UTC now time
    add .format('YYYY-MM-DD HH:mm:ss ZZ') to convert to ISO
    add .format()
    """
    return arrow.utcnow()

def startofday_epohc_now():
    """
    give the epoch of the time at 00:00 hrs in epoch
    """
    now_date = arrow.utcnow().format("YYYY-MM-DD")
    now_epoch = arrow.get(now_date).format("X")
    now_epoch = re.sub(r"\.0","000",now_epoch)
    
    return now_epoch

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


def dict_to_jsonl(dict_input):
    """
    takes a dict object and turns it into a jsonl doc
    """

    jsonl_contents = json.dumps(dict_input)
    jsonl_contents = re.sub(f"\n","",jsonl_contents)
    return jsonl_contents


def list_of_dicts_to_jsonl(list_input):
    """
    takes a list of dict objects and turns it into a jsonl doc
    """

    jsonl_contents = ""
    for each_entry in list_input:
        jsonl_contents = jsonl_contents + "\n" + json.dumps(each_entry)

    
    return jsonl_contents


def write_to_storage(data, bucket, filename_path):
    """"
    will write data to a storage location
    """
    print("performing putObject")
    client = boto3.client('s3')
    return client.put_object(Body=data, Bucket=bucket, Key=filename_path)
    
def read_from_storage(bucket, filename_path):
    """
    will read data from a storage location *s3
    """
    client = boto3.client('s3')
    response = client.get_object(
        Bucket=bucket,
        Key=filename_path,
    )
    return response

def notify_discord_bot(text_string):
    """
    notifies the discord webhook
    """
    DISCORD_BOT_WEBHOOK = os.getenv('DISCORD_BOT_WEBHOOK')

    list_of_messages = split_string_discord(text_string)

    for each_message in list_of_messages:
        time.sleep(.5)
        data = {
            "content": str(each_message)
        }
        response = requests.post(url=DISCORD_BOT_WEBHOOK, json=data)
        print(response)
    
    print(f"notification complete")


def split_string_discord(input_string,character_limit=1500):
    """
    splits a string into chunks for discord notifications
    """
    
    if len(input_string)<= character_limit:
        return [input_string]
    else:
        chunks = input_string.split('\n')
        messages = []
        chunk_string = ""
        for each_item in chunks:

            old_chunkstring = chunk_string
            new_chunk_string = f"{chunk_string}\n{each_item}"

            if len(new_chunk_string) > character_limit:
                messages.append(old_chunkstring)
                chunk_string = each_item
            elif each_item == chunks[-1]:
                print("last message")
                messages.append(chunk_string)
            else:
                chunk_string = new_chunk_string 
            
        
        return messages


def batch_send_to_sqs(coin_list,days=1):
    """
    uses batch mode for sqs send to allow 10 coins to be queued per
    """
    sqs = boto3.client('sqs')

    # queue = sqsResource.get_queue_by_name(QueueName='coin-watch-list')
    SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')
    maxBatchSize = 1 #current maximum allowed is 10
    chunks = [coin_list[x:x+maxBatchSize] for x in range(0, len(coin_list), maxBatchSize)]
    time_to_wait = 0
    time_to_wait_interval = 2 #seconds
    for chunk in chunks:
        
        entries = []
        for x in chunk:
            entry = {
                    'Id': str(x),
                    'MessageBody': 'Sent for coin analysis', 
                     #'MessageGroupId': 'coin-getter',
                     #'MessageDeduplicationId': str(x),
                     'MessageAttributes': {
                        'coin_id': {
                            'DataType': 'String',
                            'StringValue': str(x)
                        },
                        'days': {
                            'DataType': 'String',
                            'StringValue': str(days)
                        }
                     }
            }
            entries.append(entry)
            wait_time = time_to_wait + time_to_wait_interval
        response = sqs.send_message_batch(QueueUrl=SQS_QUEUE_URL,Entries=entries)
        print(response)

def send_to_sqs(coin_id):
    """
    send a message to the sqs queue specified by the environment variable
    """
    # Create SQS client
    sqs = boto3.client('sqs')

    SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        DelaySeconds=0,
        MessageGroupId="coin-getter",
        MessageDeduplicationId=str(coin_id),
        MessageAttributes={
            'coin_id': {
                'DataType': 'String',
                'StringValue': str(coin_id)
            }
        },
        MessageBody=(
            'Sent for coin analysis'
        )
    )

    print(response['MessageId'])

def dynamo_put_coin(coin_id, days, dynamodb=None):
    
    table = dynamodb.Table('watchlist')
    response = table.put_item(
       Item={
            'year': year,
            'title': title,
            'info': {
                'plot': plot,
                'rating': rating
            }
        }
    )
    return response


# send_to_sqs(str("bitcoin"))
# send_to_sqs(str("SurfMoon"))

# mylist = ["shibgf"]
# batch_send_to_sqs(mylist,days='max')


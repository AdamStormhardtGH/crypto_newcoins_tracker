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

def partition_path_from_date(input_date):
    """
    returns path for s3 partitioning from date:
    eg.
    `2021-11-27 00:00:00`
    becomes: 
    `year=2021/month=11/day=27`
    """
    date_value = arrow.get(input_date) #expects timestamp
    year = date_value.year
    month = date_value.month
    day = date_value.day

    return f"year={year}/month={month}/day={day}"


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
    chunks = input_string.split('\n')
    
    print(chunks)

    messages = []
    chunk_string = ""
    for each_item in chunks:
        old_chunkstring = chunk_string
        new_chunk_string = f"{chunk_string}\n{each_item}"
        if len(new_chunk_string) > character_limit:
            messages.append(old_chunkstring)
            chunk_string = each_item
        else:
            chunk_string = new_chunk_string 
        if each_item == chunks[-1]:
            print("last message")
            messages.append(chunk_string)
    
    return messages

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
        # DelaySeconds=1,
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


def read_sqs_message(sqs_payload, key_to_find="coin_id", delivery_method="push"):
    """
    will read sqs messages and return the body message 
    There are multiple ways to parse messages from sqs, so we need to be aware of the deliverymethod
    delivery_method:
    "pull" - we're pulling from the queue
    "push" - we're being pushed the data via like a lambda trigger
    """
    
    if delivery_method == "push":
        data = sqs_payload["Records"][0]["messageAttributes"][key_to_find]["stringValue"]
    elif delivery_method == "pull":
        data = sqs_payload["Messages"][0]["MessageAttributes"][key_to_find]["StringValue"]
    else:
        raise Exception(f"Unable to read data from sqs - delivery method {delivery_method} not supported")

    # ["MessageAttributes"][key_to_find]["Value"]
    # key_we_need = body["MessageAttributes"][key_to_find]["Value"]
    return data

def delete_message_from_queue(ReceiptHandle):
    """
    will delete a message from the sqs queue
    response = client.delete_message(
        QueueUrl='string',
        ReceiptHandle='string'
    )
    """
    sqs = boto3.client('sqs')
    SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

    response = sqs.delete_message(
        QueueUrl=SQS_QUEUE_URL,
        ReceiptHandle=ReceiptHandle
    )
    return response

def read_from_sqs_queue():
    """
    will read a message from the sqs queue
    apparently this can be unreliable, so we should try mulitple times. 
    eg. 5 times
    """
    sqs = boto3.client('sqs')

    SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

    retries = 0
    retries_max = 5
    data_found = False
    attempt_id = f"{arrow.utcnow().format('X')}-getcoin"
    data_from_message = None
    while retries < retries_max and data_found == False:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            AttributeNames=[
                
            ],
            MessageAttributeNames=[
                'coin_id',
            ],
            MaxNumberOfMessages=1,
            VisibilityTimeout=123,
            WaitTimeSeconds=10,
            ReceiveRequestAttemptId=attempt_id
        )
        try:
            data_from_message = read_sqs_message(sqs_payload=response, key_to_find="coin_id", delivery_method="pull") #["Messages"][0]["MessageAttributes"]["coin_id"]["StringValue"]
            data_found = True
            print(f"FOUND {data_from_message}")
        except:
            print("did not find")
            retries = retries + 1


    return data_from_message


    # except Exception as e:
    #     print(f"unable to parse {key_to_find} from sqs message: {sqs_payload} ")
    # exit()


# send_to_sqs('adam')
# read_from_sqs_queue()
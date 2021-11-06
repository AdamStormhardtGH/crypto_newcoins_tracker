import utils
import get_coins
import time


def lambda_handler(sqs_event, context="none"):   
    """
    main orchestration executable for coin getter.
    Runs the job with a string as event
    """
    coin_id = utils.read_sqs_message(sqs_event)

    if len(str(coin_id))==0:
        print("coin not included in request. Exiting...")
        exit()
    else:
        try:
            return get_coins.orchestrate_coin_getter(coin_id=coin_id, days=1)
        except Exception as e:
            print(f"error getting coin: {e}")


# my_message = {'Records': [{'messageId': '3e58d5aa-7ba3-4e81-8dee-7265e874039d', 'receiptHandle': 'AQEBtM2sgzri0HhtDCYvRxuCoedswCNjcqVEzmKqSGBMnlon4yAjEUBArZAtIVspicSp/cittcfGl8BQTm29/bldPOyiqtHa81ySuKHO3oUW9dUILFNNogM6LR3KMskOsI4yS26qgdK/RSuYyJdxrkoc1Tof7xO68Csl3qzHt+Iw23OsrN9Sk/k7Wp8L8JJJ8oQYjt6Bi7CYhXXGM85BBBYTAw0O+pePHEkz86GGZelqho1T9YYePWyFHlWS3JQJ2kDOS47jNYd48w+4GQs9it/Gcn9loZNnVpR8jE3dgRYvIeY=', 'body': '{\n  "Type" : "Notification",\n  "MessageId" : "15e69bf2-9993-52d4-9090-c1f2dfd8e0fe",\n  "SequenceNumber" : "10000000000000007000",\n  "TopicArn" : "arn:aws:sns:us-east-1:405595038722:sns-coin-watchlist.fifo",\n  "Message" : "blah",\n  "Timestamp" : "2021-11-06T08:59:55.767Z",\n  "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:405595038722:sns-coin-watchlist.fifo:3c9e3974-5251-4ae2-9595-4d74854d5f38",\n  "MessageAttributes" : {\n    "coin_id" : {"Type":"String","Value":"bitcoin"}\n  }\n}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1636189196274', 'SequenceNumber': '18865608507955695616', 'MessageGroupId': '123', 'SenderId': 'AIDAYRRVD2ENU4DSO2WBX', 'MessageDeduplicationId': '1233', 'ApproximateFirstReceiveTimestamp': '1636189197290'}, 'messageAttributes': {}, 'md5OfBody': '68d887d21700682672af18c70ebd02b0', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-east-1:405595038722:coin-watch-list.fifo', 'awsRegion': 'us-east-1'}]}
# print(lambda_handler(my_message,""))
# lambda_handler("bitcoin","")
# utils.notify_discord_bot("report")


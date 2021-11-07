import utils
import get_coins
import time


def lambda_handler(sqs_event, context="none"):   
    """
    main orchestration executable for coin getter.
    Runs the job with a string as event
    """
    coin_id = utils.read_sqs_message(sqs_event,key_to_find="coin_id")
    try:
        days = utils.read_sqs_message(sqs_event,key_to_find="days")
    except:
        days = 1


    if len(str(coin_id))==0:
        print("coin not included in request. Exiting...")
        return "coin not included in request"
    else:
        
        return get_coins.orchestrate_coin_getter(coin_id=coin_id, days=days)
        # except Exception as e:
        #     print(f"error getting coin: {e}")



# print(lambda_handler(my_message,""))
# lambda_handler("bitcoin","")
# utils.notify_discord_bot("report")



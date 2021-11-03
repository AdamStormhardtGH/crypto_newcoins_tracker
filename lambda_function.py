from re import U
from src import marketsnapshot
from src import compareyesterday
from src import getwatchlistdetails
from src import utils
import time


def lambda_handler(event, context):   
    """
    main orchestration executable.
    Runs the job
    """
    #get snapshot for the market
    marketsnapshot.get_market_snapshot()
    time.sleep(1)

    #compare today's market snapshot to yesterday
    new_coins = compareyesterday.compare_yesterday_and_today()
    # time.sleep(1)

    #now get new stuff for watch lists
    coins_checked = getwatchlistdetails.orchestrate_watchlist_details_check()
    
    new_coins_formatted = ""
    for each in new_coins:
        new_coins_formatted = f"{new_coins_formatted}\n - {each}"

    watched_coins_formatted = ""
    for each_watched_coin in coins_checked:
        
        if each_watched_coin['age'] >=1:
            price = "{:.12f}".format(each_watched_coin['prices'])
            buy = ""
            if each_watched_coin['prices'] <0.003 and each_watched_coin['total_volumes'] > 1300000:
                buy = "🔥"
            watched_coins_formatted = f"{watched_coins_formatted}{each_watched_coin['id']} - ({each_watched_coin['age']}d old) | 24hr vol: ${round(each_watched_coin['total_volumes']/1000000,2)} Million at ${price} {buy}\n"

    report = f"""
    {utils.datetime_now().format()}(UTC)\n**New Coins: {len(new_coins)}**{new_coins_formatted} \n\n**Watched Coins**\n{watched_coins_formatted}"""

    utils.notify_discord_bot(report)

    print(report)
    print( "completed job ")


# lambda_handler("yo","")
# utils.notify_discord_bot("report")


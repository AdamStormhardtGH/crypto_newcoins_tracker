from re import U
from src import marketsnapshot
from src import compareyesterday
from src import getwatchlistdetails
from src import utils


def lambda_handler(event, context):   
    """
    main orchestration executable.
    Runs the job
    """
    #get snapshot for the market
    marketsnapshot.get_market_snapshot()

    #compare today's market snapshot to yesterday
    new_coins = compareyesterday.compare_yesterday_and_today()

    #now get new stuff for watch lists
    coins_checked = getwatchlistdetails.orchestrate_watchlist_details_check()
    
    new_coins_formatted = ""
    for each in new_coins:
        new_coins_formatted = f"{new_coins_formatted}\n - {each}"

    watched_coins_formatted = ""
    for each_watched_coin in coins_checked:
        price = "{:.12f}".format(each_watched_coin['prices'])
        watched_coins_formatted = f"{watched_coins_formatted}{each_watched_coin['id']} - 24hr volume: ${round(each_watched_coin['total_volumes']/1000000,2)} Million at ${price}\n"

    report = f"""
    {utils.datetime_now().format()}(UTC)\n**New Coins: {len(new_coins)}**{new_coins_formatted} \n\n**Watched Coins**\n{watched_coins_formatted}"""
    utils.notify_discord_bot(report)

    return "completed job "


lambda_handler("yo",{})
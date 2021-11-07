"""
will pull details for a specific coin from an API (coingecko)
and write to s3 based on environment variables
"""
from pycoingecko import CoinGeckoAPI
import cgutils
import os, time
from dotenv import load_dotenv
load_dotenv()


def orchestrate_coin_getter(coin_id, days=1):
    """
    orchestrate the getter of coins. 
    Deal with single and multiple days
    """
    print(f"coin_id: {coin_id}")
    try: 
        BUCKET = os.getenv('BUCKET')
        COIN_MARKET_DATA_PATH = os.getenv('COIN_MARKET_DATA_PATH')
    except Exception as e:
        print(f"error initializing coin getter environments: {e}")

    
    coin_data_raw = get_coin(coin_id=coin_id, days=days) #this is a list
    if len(coin_data_raw) == 0:
        print("no data for coin. Exiting")
        return None
    else:
        print("got coin history. Writing to s3...")
        coin_path_latestdate = coin_data_raw[-1]["date"]
        date_partition = cgutils.partition_path_from_date(coin_path_latestdate)
        coin_path = f"{COIN_MARKET_DATA_PATH}/{date_partition}/{coin_path_latestdate}_{coin_id}.json"
        print(f"coin path = {coin_path}")
        coin_data_jsonl = cgutils.list_of_dicts_to_jsonl(coin_data_raw)
        s3write_status = cgutils.write_to_storage(data=coin_data_jsonl, bucket=BUCKET,filename_path=coin_path)
        print(s3write_status)
    return s3write_status
    

def get_coin(coin_id,days=1):
    """
    get the coin from the api
    defaults to single day
    days option 1,2, 3, 30, max
    returns list of items
    """
    print(f"getting coin details for: {coin_id}")
    time.sleep(1.1)
    if days != 'max':
        days = int(days)
    cg = CoinGeckoAPI()

    try:
        coin_details = cg.get_coin_market_chart_by_id(id=coin_id,vs_currency="aud", days=days, interval="daily")  #get the 24 hour 
    except ValueError:
        return []
    ### retry logic - disabled to see if we can let lambda deal with this with retry
    # succeeded = False
    # retries = 0
    # max_retries = 4
    # while succeeded == False or retries < max_retries:
    #     try:
    #         coin_details = cg.get_coin_market_chart_by_id(id=coin_id,vs_currency="aud", days=days, interval="daily")  #get the 24 hour 
    #         succeeded = True
    #     except Exception as e:
    #         print(e)
    #         time.sleep(1)
    #         retries = retries + 1
    
    # print(coin_details)
    
    format_extracted_coin_details = extract_historical_market_value_for_coins(coin_details,coin_id=coin_id,days=days)

    return format_extracted_coin_details


def extract_historical_market_value_for_coins(coin_details,coin_id,days):

    print("extract_historical_market_value_for_coins()")
    end_entry = -1 #the entry which isn't the time at the call - looks like range uses the last item the same as a < symbol. 
    # if days == 'max':
    #     coins_to_get_startingpoint = 0
    # else: 
    #     coins_to_get_startingpoint = end_entry-days
    coins_to_get_startingpoint = 0
    coin_history = []

    #apply the indexing based on start and end
    coin_index = []
    print(coin_details["prices"][coins_to_get_startingpoint:end_entry])
    for eachindex in coin_details["prices"][coins_to_get_startingpoint:end_entry]:
        # print(eachindex)
        coin_index.append(coin_details["prices"].index(eachindex))

    for each_entry in coin_index:
        coin_data = {
            "id": coin_id,
            "date": cgutils.epoch_to_timestamp(coin_details["prices"][each_entry][0]), #was -1 for latest. lets just get the minight volume
            "prices": coin_details["prices"][each_entry][-1],
            "market_caps": coin_details["market_caps"][each_entry][-1],
            "total_volumes": coin_details["total_volumes"][each_entry][-1]
            # "age": len(coin_details["total_volumes"])-2
        }
        coin_history.append(coin_data)
    
    return coin_history



# print(get_coin("pizza-pug-coin","max"))
# print(orchestrate_coin_getter("shiba","max") )

# print(get_coin("spookyshiba", days='max') )
# orchestrate_coin_getter("spookyshiba",days="max")

# coin_list = ['arabtycoon', 'babyxape', 'nowlage-coin', 'chimeras', 'hackleberry', 'pizza-pug-coin', 'ardana', 'burgerburn', 'flokiloki', 'hector-dao', 'hellsing-inu', 'bit2me', 'bitorbit', 'puppy-token', 'tiger-baby', 'boorio', 'chilliswap', 'corsac', 'crazy-bunny-equity-token', 'fsd-coin', 'ghospers-game', 'idle-cyber', 'idm-token', 'novaxcrystal', 'pixelpotus', 'polyunity-finance', 'rivrshiba', 'rugpull-prevention', 'sadbaby', 'arcanineinu', 'cosmostarter', 'cropbytes', 'hedge-finance', 'legend-of-fantasy-war', 'memewars', 'pomerocket', 'shibamon', 'yokai-money', 'baby-floki-up', 'buffedshiba', 'master-usd', 'pappay', 'mommyusdt', 'smart-coin-smrtr', 'biden', 'bunscake', 'goosefx', 'squidanomics', 'stardust', 'coin-of-nature', 'wolverine', 'chain', 'exodia', 'memecoinfactorytoken', 'ninja-fantasy-token', 'onerare', 'royalada', 'schrodinger', 'shiborg-inu', 'stabilize-token', 'terra-world-token', 'yohero', 'bake-up', 'farmerdoge', 'gemit-app', 'kiba-inu-bsc', 'lilflokiceo', 'lizard-token', 'samsunspor-fan-token', 'solalambo', 'sunshield', 'avaterra', 'cryptoforspeed', 'granny-shiba', 'memecoin-factory', 'shib-army', 'ultrachad', 'god-shiba-token', 'ryze-inu', 'bking-finance', 'blockster', 'hanagold-token', 'lil-doge-floki-token', 'maga-coin', 'mousepad', 'oobit', 'sparklab', 'arrb-token', 'boom-shiba', 'cross-chain-bch', 'fantom-cake', 'gmcoin-2', 'nest-egg', 'novaxmetal', 'oink-token', 'olympus-inu-dao', 'orenda-protocol', 'phoenix-unity', 'quidd', 'saint-inu', 'shibanomi', 'spartacus', 'automaticup', 'big-eth', 'dogerocket', 'genesis-worlds', 'ginspirit', 'mgoat', 'redzilla', 'surfmoon', 'huckleberry', 'liquid-collectibles', 'meta-floki', 'metashib-token', 'reward-cycle', 'saveplanetearth-old', 'yandere-shiba', 'zoo-labs', 'clout-art', 'fydcoin', 'lil-doge-floki', 'maggot', 'meals', 'shibu-life', 'shokky', 'treat', 'baby-schrodinger-coin', 'merkle-network', 'profit-bank', 'sleepearn-finance', 'blocks', 'chihiro-inu', 'decentsol', 'dogekongzilla', 'energy8', 'enno-cash', 'great-bounty-dealer', 'mirai-token', 'mystic-warrior', 'nekoinu', 'novaxsolar', 'pumpshibax', 'shibgf', 'shibosu', 'stabilize-usd', 'wolfecoin', 'dyor-token', 'ethernaal', 'footballgo', 'immutable-x', 'koromaru', 'neet-finance', 'nelo-metaverse', 'odindao', 'olympic-doge', 'polkainu', 'shockwave-finance', 'vpunks-token', 'afrostar', 'flokimars', 'megacosm', 'rotten-floki', 'rocket-shib', 'apelab', 'bitsol-finance', 'fenix-finance', 'floof', 'informatix', 'island-doges', 'tanks', 'ironman', 'booster-bsc', 'cryptobay', 'disco-burn-token', 'gains-network', 'glorydoge', 'hydrolink', 'jacywaya', 'leafty', 'lucky-cat', 'mensa', 'ponyo-inu', 'pulsedoge', 'sola-ninja', 'soldoge', 'atmosphere-ccg', 'berserk-inu', 'bunnygirl', 'dragon-kart-token', 'gilgamesh-eth', 'infomatix', 'potion-brew-finance', 'urubit', 'vaultdefi', 'foreverbnb', 'justfarm', 'symbull', 'tits-token', 'titsv2', 'microdexwallet', 'entropyfi', 'space-sip', 'zam-io', 'ariadne', 'mainframe-protocol', 'omax-token', 'artverse-token', 'baby-white-hamster', 'cats-claw', 'cloud9bsc-finance', 'dxbpay', 'flokachu-token', 'meta-cat', 'mini-saitama', 'nil-dao', 'oogi', 'pension-plan', 'polyx', 'robin-inu', 'santa-coin-2', 'shiryo-inu', 'stemx', 'swole-doge', 'zerotwohm', 'ari10', 'dfsocial-gaming-2', 'dragon-battles', 'evergreen-token', 'miyazaki-inu', 'parrot-egg-polygon', 'rivrdoge', 'ryoshimoto', 'alpha-shiba-inu', 'drachma', 'ethereum-name-service', 'flash-token', 'future-real-estate-token', 'itsmyne', 'luminos-mining-protocol', 'oje-token', 'rune-shards', 'shibalite', 'xlshiba', 'luna-pad', 'shambala', '1swap', 'balisari', 'algopad', 'dogeman', 'first-inu', 'leeds-united-fan-token', 'metacat', 'mini-safemoon-inu-v2', 'nogoaltoken', 'pool-token', 'silva-token', 'smugdoge', 'spookyshiba', 'taichi', 'tractor-joe', 'catena-x', 'ginza-network', 'hyfi-token', 'levelup-gaming', 'shar-pei', 'spinada-cash', 'togashi-inu', 'daddybezos', 'egyptian-mau', 'gaming-doge', 'sakura-neko', 'shkooby-inu', 'zeloop-eco-reward', 'crypto-classic', 'fantomstarter', 'killua-inu', 'mewn-inu', 'secured-ship', 'pumpkin-punks', 'gami-world', 'mines-of-dalarnia', 'oec-token', 'skylight', 'bebop-inu', 'enterbutton', 'feedeveryshiba', 'floki-one', 'godzilla', 'kiba', 'marsx', 'meta-doge', 'metaplay', 'moonka', 'snake-token', 'squid', 'unityventures', 'cardanomics', 'game-coin', 'mega-shiba-inu', 'punch', 'scorpion-finance', 'xeus']

# import time
# for each in coin_list:
#     try:
#         time.sleep(1)
#         orchestrate_coin_getter(each,days='max')
#     except Exception as e:
#         print(e)

# cg = CoinGeckoAPI()
# for each in range(0,100):
#     coin_details = cg.get_coin_market_chart_by_id(id="bitcoin",vs_currency="aud", days=1, interval="daily") 
#     print(coin_details)







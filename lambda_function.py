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

    # #compare today's market snapshot to yesterday
    new_coins = compareyesterday.compare_yesterday_and_today()
    time.sleep(1)
    # new_coins = []

    #now get new stuff for watch lists
    coins_checked = getwatchlistdetails.orchestrate_watchlist_details_check()
    # getwatchlistdetails.queue_coins_to_get()
    
    new_coins_formatted = ""
    for each in new_coins:
        new_coins_formatted = f"{new_coins_formatted}\n - {each}"

    highvolume_value = 100000000 #1300000
    watched_coins_formatted = ""
    sorted_list = sorted(coins_checked, key=lambda d: d['total_volumes'], reverse = True) 
    top_coins_num = 10
    top_coins = sorted_list[0:top_coins_num]
    #top 5 coins today by volume
    for each_watched_coin in top_coins:
        
        if each_watched_coin['age'] >=1 and each_watched_coin['age']<13:
            price = "{:.12f}".format(each_watched_coin['prices'])
            buy = ""
            # if each_watched_coin['prices'] <0.003 and each_watched_coin['total_volumes'] > highvolume_value:
            if each_watched_coin['total_volumes'] > highvolume_value:
                buy = "🌙"
            watched_coins_formatted = f"{watched_coins_formatted}{each_watched_coin['id']} - ({each_watched_coin['age']}d old) | 24hr vol: ${round(each_watched_coin['total_volumes']/1000000,2)} Million at ${price} {buy}\n"

    report = f"""
    {utils.datetime_now().format()}(UTC)\n**New Coins: {len(new_coins)}**{new_coins_formatted} \n\n**Top Watched Coins**\n{watched_coins_formatted}"""
    # {utils.datetime_now().format()}(UTC)\n**New Coins: {len(new_coins)}**{new_coins_formatted} \n\n

    utils.notify_discord_bot(report)
    print( "completed daily update of coins job ")
    return(report)



# lambda_handler("execute","")c
# utils.notify_discord_bot("report")

# getwatchlistdetails.queue_coins_to_get(days='max')
# print(getwatchlistdetails.get_watch_list())

# coin_list = ['arabtycoon', 'babyxape', 'nowlage-coin', 'chimeras', 'hackleberry', 'pizza-pug-coin', 'ardana', 'burgerburn', 'flokiloki', 'hector-dao', 'hellsing-inu', 'bit2me', 'bitorbit', 'puppy-token', 'tiger-baby', 'boorio', 'chilliswap', 'corsac', 'crazy-bunny-equity-token', 'fsd-coin', 'ghospers-game', 'idle-cyber', 'idm-token', 'novaxcrystal', 'pixelpotus', 'polyunity-finance', 'rivrshiba', 'rugpull-prevention', 'sadbaby', 'arcanineinu', 'cosmostarter', 'cropbytes', 'hedge-finance', 'legend-of-fantasy-war', 'memewars', 'pomerocket', 'shibamon', 'yokai-money', 'baby-floki-up', 'buffedshiba', 'master-usd', 'pappay', 'mommyusdt', 'smart-coin-smrtr', 'biden', 'bunscake', 'goosefx', 'squidanomics', 'stardust', 'coin-of-nature', 'wolverine', 'chain', 'exodia', 'memecoinfactorytoken', 'ninja-fantasy-token', 'onerare', 'royalada', 'schrodinger', 'shiborg-inu', 'stabilize-token', 'terra-world-token', 'yohero', 'bake-up', 'farmerdoge', 'gemit-app', 'kiba-inu-bsc', 'lilflokiceo', 'lizard-token', 'samsunspor-fan-token', 'solalambo', 'sunshield', 'avaterra', 'cryptoforspeed', 'granny-shiba', 'memecoin-factory', 'shib-army', 'ultrachad', 'god-shiba-token', 'ryze-inu', 'bking-finance', 'blockster', 'hanagold-token', 'lil-doge-floki-token', 'maga-coin', 'mousepad', 'oobit', 'sparklab', 'arrb-token', 'boom-shiba', 'cross-chain-bch', 'fantom-cake', 'gmcoin-2', 'nest-egg', 'novaxmetal', 'oink-token', 'olympus-inu-dao', 'orenda-protocol', 'phoenix-unity', 'quidd', 'saint-inu', 'shibanomi', 'spartacus', 'automaticup', 'big-eth', 'dogerocket', 'genesis-worlds', 'ginspirit', 'mgoat', 'redzilla', 'surfmoon', 'huckleberry', 'liquid-collectibles', 'meta-floki', 'metashib-token', 'reward-cycle', 'saveplanetearth-old', 'yandere-shiba', 'zoo-labs', 'clout-art', 'fydcoin', 'lil-doge-floki', 'maggot', 'meals', 'shibu-life', 'shokky', 'treat', 'baby-schrodinger-coin', 'merkle-network', 'profit-bank', 'sleepearn-finance', 'blocks', 'chihiro-inu', 'decentsol', 'dogekongzilla', 'energy8', 'enno-cash', 'great-bounty-dealer', 'mirai-token', 'mystic-warrior', 'nekoinu', 'novaxsolar', 'pumpshibax', 'shibgf', 'shibosu', 'stabilize-usd', 'wolfecoin', 'dyor-token', 'ethernaal', 'footballgo', 'immutable-x', 'koromaru', 'neet-finance', 'nelo-metaverse', 'odindao', 'olympic-doge', 'polkainu', 'shockwave-finance', 'vpunks-token', 'afrostar', 'flokimars', 'megacosm', 'rotten-floki', 'rocket-shib', 'apelab', 'bitsol-finance', 'fenix-finance', 'floof', 'informatix', 'island-doges', 'tanks', 'ironman', 'booster-bsc', 'cryptobay', 'disco-burn-token', 'gains-network', 'glorydoge', 'hydrolink', 'jacywaya', 'leafty', 'lucky-cat', 'mensa', 'ponyo-inu', 'pulsedoge', 'sola-ninja', 'soldoge', 'atmosphere-ccg', 'berserk-inu', 'bunnygirl', 'dragon-kart-token', 'gilgamesh-eth', 'infomatix', 'potion-brew-finance', 'urubit', 'vaultdefi', 'foreverbnb', 'justfarm', 'symbull', 'tits-token', 'titsv2', 'microdexwallet', 'entropyfi', 'space-sip', 'zam-io', 'ariadne', 'mainframe-protocol', 'omax-token', 'artverse-token', 'baby-white-hamster', 'cats-claw', 'cloud9bsc-finance', 'dxbpay', 'flokachu-token', 'meta-cat', 'mini-saitama', 'nil-dao', 'oogi', 'pension-plan', 'polyx', 'robin-inu', 'santa-coin-2', 'shiryo-inu', 'stemx', 'swole-doge', 'zerotwohm', 'ari10', 'dfsocial-gaming-2', 'dragon-battles', 'evergreen-token', 'miyazaki-inu', 'parrot-egg-polygon', 'rivrdoge', 'ryoshimoto', 'alpha-shiba-inu', 'drachma', 'ethereum-name-service', 'flash-token', 'future-real-estate-token', 'itsmyne', 'luminos-mining-protocol', 'oje-token', 'rune-shards', 'shibalite', 'xlshiba', 'luna-pad', 'shambala', '1swap', 'balisari', 'algopad', 'dogeman', 'first-inu', 'leeds-united-fan-token', 'metacat', 'mini-safemoon-inu-v2', 'nogoaltoken', 'pool-token', 'silva-token', 'smugdoge', 'spookyshiba', 'taichi', 'tractor-joe', 'catena-x', 'ginza-network', 'hyfi-token', 'levelup-gaming', 'shar-pei', 'spinada-cash', 'togashi-inu', 'daddybezos', 'egyptian-mau', 'gaming-doge', 'sakura-neko', 'shkooby-inu', 'zeloop-eco-reward', 'crypto-classic', 'fantomstarter', 'killua-inu', 'mewn-inu', 'secured-ship', 'pumpkin-punks', 'gami-world', 'mines-of-dalarnia', 'oec-token', 'skylight', 'bebop-inu', 'enterbutton', 'feedeveryshiba', 'floki-one', 'godzilla', 'kiba', 'marsx', 'meta-doge', 'metaplay', 'moonka', 'snake-token', 'squid', 'unityventures', 'cardanomics', 'game-coin', 'mega-shiba-inu', 'punch', 'scorpion-finance', 'xeus']
# coin_list_small = ['arabtycoon', 'babyxape', 'nowlage-coin', 'chimeras', 'hackleberry', 'pizza-pug-coin', 'ardana', 'burgerburn', 'flokiloki', 'hector-dao', 'hellsing-inu', 'bit2me', 'bitorbit', 'puppy-token', 'tiger-baby', 'boorio', 'chilliswap', 'corsac', 'crazy-bunny-equity-token', 'fsd-coin', 'ghospers-game', 'idle-cyber', 'idm-token', 'novaxcrystal', 'pixelpotus', 'polyunity-finance', 'rivrshiba', 'rugpull-prevention', 'sadbaby', 'arcanineinu', 'cosmostarter', 'cropbytes', 'hedge-finance', 'legend-of-fantasy-war', 'memewars', 'pomerocket', 'shibamon', 'yokai-money', 'baby-floki-up', 'buffedshiba', 'master-usd', 'pappay', 'mommyusdt', 'smart-coin-smrtr', 'biden', 'bunscake', 'goosefx', 'squidanomics', 'stardust', 'coin-of-nature', 'wolverine', 'chain', 'exodia', 'memecoinfactorytoken', 'ninja-fantasy-token', 'onerare', 'royalada', 'schrodinger', 'shiborg-inu', 'stabilize-token', 'terra-world-token', 'yohero', 'bake-up', 'farmerdoge', 'gemit-app', 'kiba-inu-bsc', 'lilflokiceo', 'lizard-token', 'samsunspor-fan-token', 'solalambo', 'sunshield', 'avaterra', 'cryptoforspeed']
# print(len(coin_list))
# utils.batch_send_to_sqs(coin_list_small,days='max')





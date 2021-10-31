# overview



## Job 1 - Pull Market list snapshot of all avaialable coins

`marketsnapshot.get_market_snapshot()`

1. Get list of all available coins ( /coins/list)
2. add a timestamp for us to track dates
3. output as json line delimited data to s3/gcp
4. return success or failure

## Job 2 - Compare with yesterday to find new coins

`compareyesterday.compare_yesterday_and_today()`

This job will check the bucket path associated with the time of execution (UTC)
eg. if execution at midnight UTC on November 11, 2021, the path will look for:
 `<bucket>/marketlist/2021-11-11-coinlist.json` - today
 `<bucket>/marketlist/2021-11-10-coinlist.json` - yesterday

TODO:
- Fallback to prior day if path does not exist x3 days
- graceful exit if no comparison date exists

1. Loads today's market list snapshop based on execution date
2. Loads yesterday's market list snapshop based on execution date
3. Compares the 2 sets of data, looking for new coins which were not in Yesterday's list
4. Adds today's timestamp into the payload
5. Writes the output of entries into a 'watch' list bucket `<bucket>/watchlist/2021-11-11-newcoins.json`
4. return success or failure


## Job 3 - Pull Today's Details for watched coins

This job will pull the market price and other details like volume etc for a specific coin and for each 



--------

## Setting up for lambda deployment

run `pip install -r requirements.txt --target ./package` to install all required packages listed in the requirements.txt to a local directory. This helps us deploy a zip
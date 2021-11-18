"""
script for the ec2 instance to run daily updates and do its notifcation etc
run this on a cron
"""

import lambda_function
from src import daily_check

lambda_function.lambda_handler("daily","")
daily_check.orchestrate_daily_coin_check()

print("finished daily update")
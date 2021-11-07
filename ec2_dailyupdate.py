"""
script for the ec2 instance to run daily updates and do its notifcation etc
run this on a cron
"""

import lambda_function

lambda_function.lambda_handler("daily","")

print("finished daily update")
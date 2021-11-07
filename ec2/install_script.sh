#!/bin/bash

#in /home/ec2-user/

sudo yum update -y
sudo yum install git -y

cd /home/ec2-user/
git clone https://github.com/AdamRuddGH/crypto_newcoins_tracker.git 
cd crypto_newcoins_tracker
pip3 install -r requirements.txt
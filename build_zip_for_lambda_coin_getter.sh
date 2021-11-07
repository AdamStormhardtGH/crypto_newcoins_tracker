#!/bin/bash

# This script will build a .zip file which is ready to be deployed to lambda
# This will move to cloudformation and build systems once we move to a ci/cd environment

#ensure you have ownership 
# chmod 775 ./build_zip_for_lambda.sh
echo "building lambda zip for coin_getter"
rm -rf ./zip_builds/coin_getter/**
echo "Deleted content in the builds directory.\n Rebuilding..."
mkdir ./zip_builds/coin_getter/files/
cp -R ./src/coin_getter/ ./zip_builds/coin_getter/files/
echo "Project files copied. Installing packages..."
pip install -r requirements.txt --target ./zip_builds/coin_getter/files/
echo "Copy complete. Zipping..."
cd ./zip_builds/coin_getter/files/
zip -r ../coin-getter-lambda-package.zip .
cd ..
rm -rf ./files/**
echo "Complete"
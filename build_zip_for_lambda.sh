#!/bin/bash

# This script will build a .zip file which is ready to be deployed to lambda
# This will move to cloudformation and build systems once we move to a ci/cd environment

#ensure you have ownership 
# chmod 775 ./build_zip_for_lambda.sh

rm -rf ./zip_builds/**
echo "Deleted content in the builds directory.\n Rebuilding..."
mkdir ./zip_builds/files/
cp -R ./src ./zip_builds/files/
cp ./lambda_function.py ./zip_builds/files/
echo "Project files copied. Installing packages..."
pip install -r requirements.txt --target ./zip_builds/files/
echo "Copy complete. Zipping..."
cd ./zip_builds/files/
zip -r ../deployment-package.zip .
rm -rf ./zip_builds/files/**
echo "Complete"
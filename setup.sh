#!/bin/bash

cd lambda_src
zip ../function.zip lambda_hello_world.py
cd ..

aws --endpoint-url=http://localhost:4566 \
lambda create-function --function-name lambda-hello-world \
--zip-file fileb://function.zip \
--handler lambda_hello_world.handler --runtime python3.9 \
--role arn:aws:iam:us-east-1:000000000000:role/lambda-role 

aws --endpoint-url=http://localhost:4566 \
s3api put-bucket-notification-configuration --bucket davis-test-bucket \
--notification-configuration file://s3-notif-config.json
#!/bin/bash

cd lambda_src
zip ../function.zip lambda_crud.py
cd ..

aws --endpoint-url=http://localhost:4566 \
lambda create-function --function-name lambda_crud \
--zip-file fileb://function.zip \
--handler lambda_crud.handler --runtime python3.9 \
--role arn:aws:iam:us-east-1:000000000000:role/lambda-role 

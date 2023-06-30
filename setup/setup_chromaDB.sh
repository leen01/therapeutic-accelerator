#!/usr/bin/env bash

# setup chroma DB
export AWS_ACCESS_KEY_ID=****************
export AWS_SECRET_ACCESS_KEY=**********************
export AWS_REGION=us-east-1

# Chroma publishes Cloudformation templates to S3 for each release.
aws cloudformation create-stack --stack-name my-chroma-stack --template-url https://s3.amazonaws.com/public.trychroma.com/cloudformation/latest/chroma.cf.json

# You can get the public IP address of your new Chroma server using the AWS console, or using the following command:
aws cloudformation describe-stacks --stack-name my-chroma-stack --query 'Stacks[0].Outputs'

# Customize the stack example
# aws cloudformation create-stack --stack-name my-chroma-stack --template-url https://s3.amazonaws.com/public.trychroma.com/cloudformation/latest/chroma.cf.json \
#     --parameters ParameterKey=KeyName,ParameterValue=mykey \
#                  ParameterKey=InstanceType,ParameterValue=m5.4xlarge

# Configure Chroma Library (2 Ways):
# 1. Using environmental variables
export CHROMA_API_IMPL=rest
export CHROMA_SERVER_HOST=<server IP address>
export CHROMA_SERVER_HTTP_PORT=8000

# 2. Using python
# import chromadb
# from chromadb.config import Settings

# chroma = chromadb.Client(Settings(chroma_api_impl="rest",
#                                   chroma_server_host="<server IP address>",
#                                   chroma_server_http_port=8000))

# To destroy the stack and remove all AWS resources, use the AWS CLI delete-stack command.
# aws cloudformation delete-stack --stack-name my-chroma-stack
import logging
from botocore.exceptions import ClientError
import boto3

AWS_REGION = 'us-east-1'
LOCALSTACK_INTERNAL_ENDPOINT_URL = 'http://host.docker.internal:4566'
ENDPOINT_URL = 'http://localhost:4566'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

s3_client = boto3.client("s3", region_name=AWS_REGION, endpoint_url=LOCALSTACK_INTERNAL_ENDPOINT_URL)

def create_bucket(bucket_name):
    
    try:
        resp = s3_client.create_bucket(Bucket=bucket_name)
    except ClientError as err:
        logger.exception(f'Unable to create  S3 bucket locally. Error : {err}')
    else: return resp


def handler(event, context):
    
    bucket_dat = event['Records'][0]['s3']['bucket']
    file_dat = event['Records'][0]['s3']['object']
     
    logger.warning(f'You created {file_dat["key"]} in {bucket_dat["name"]}\n')
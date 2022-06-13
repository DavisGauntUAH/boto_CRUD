import glob
import json
import logging
import boto3
from botocore.exceptions import ClientError
import os

from requests import delete

AWS_REGION = os.environ.get('AWS_REGION')
AWS_PROFILE = os.environ.get('AWS_PROFILE')
ENDPOINT_URL = os.environ.get('LOCALSTACK_ENDPOINT_URL')

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

boto3.setup_default_session(profile_name=AWS_PROFILE)
s3_client = boto3.client("s3", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
s3_resource = boto3.resource("s3", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)


def create_bucket(bucket_name):
    
    try:
        resp = s3_client.create_bucket(Bucket=bucket_name)
    except Exception as err:
        logger.exception(f'Unable to create  S3 bucket locally. Error : {err}')
    else: return resp
    
    
def empty_bucket(b_name):
    
    try:
        bucket = s3_resource.Bucket(b_name)
        resp = bucket.objects.all().delete()
    except Exception as err:
        logger.exception(f'Error : {err}')
        raise
    
    
def del_bucket(b_name):
    
    try:
        empty_bucket(b_name)
        resp = s3_client.delete_bucket(Bucket=b_name)
    except Exception as err:
        logger.exception(f'Error: could not delete bucket: {err}')
    else:
        return resp
    
    
def del_file(b_name, f_name):
    
    try:
        s3_resource.Object(b_name, f_name).delete()
    except Exception as err:
        logger.exception(f'Error: could not delete File: {err}')
        
    
    
def upload_file(f_name, bucket, obj_name=None):
    
    try:
        if obj_name is None: obj_name = os.path.basename(f_name) 
        resp = s3_client.upload_file(f_name, bucket, obj_name)
    except ClientError as err:
        logger.exception (f'Error: could not Upload file to {bucket}: {err}')
    else:
        return resp
    
    
def list_bucket_contents(b_name):
    try:
        bucket = s3_resource.Bucket(b_name)
        resp = []
        for obj in bucket.objects.all():
            resp.append(obj.key)
    except Exception as err:
        logger.exception(f'Error: {err}')
    else:
        return resp


def main():
    
    b_name = 'davis-crud-bucket'
    
    logger.info('Creating S3 bucket on localy ...')
    s3_log = create_bucket(b_name)
    logger.info(json.dumps(s3_log, indent=4)+ '\n')
    
    files = glob.glob('./import/*.txt')
    for file in files:
        upload_file(file, b_name)
        
    s3_log = list_bucket_contents(b_name)
    logger.info(s3_log)
    
    del_file(b_name, 'file1.txt')
    s3_log = list_bucket_contents(b_name)
    logger.info(s3_log)    
    
#    time.sleep(2)
#    del_bucket(b_name)


if __name__ == '__main__':
    main()
import logging
import os
from botocore.exceptions import ClientError
import boto3

AWS_REGION = 'us-east-1'
LOCALSTACK_INTERNAL_ENDPOINT_URL = 'http://host.docker.internal:4566'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

def create_bucket(bucket_name, s3):
    
    try:
        resp = s3.create_bucket(Bucket=bucket_name)
    except ClientError as err:
        logger.exception(f'Unable to create  S3 bucket locally. Error : {err}')
    else: return resp


def empty_bucket(b_name, s3):
    
    try:
        bucket = s3.Bucket(b_name)
        resp = bucket.objects.all().delete()
    except Exception as err:
        logger.exception(f'Error : {err}')
        raise
    
    
def del_bucket(b_name, s3):
    
    try:
        empty_bucket(b_name, s3)
        resp = s3.delete_bucket(Bucket=b_name)
    except Exception as err:
        logger.exception(f'Error: could not delete bucket: {err}')
    else:
        return resp
    
    
def del_file(b_name, f_name, s3):
    
    try:
        s3.Object(b_name, f_name).delete()
    except Exception as err:
        logger.exception(f'Error: could not delete File: {err}')
        
    
    
def upload_file(f_name, bucket, s3, obj_name=None):
    
    try:
        if obj_name is None: obj_name = os.path.basename(f_name) 
        resp = s3.upload_file(f_name, bucket, obj_name)
    except ClientError as err:
        logger.exception (f'Error: could not Upload file to {bucket}: {err}')
    else:
        return resp
    
    
def list_bucket_contents(b_name, s3):
    try:
        bucket = s3.Bucket(b_name)
        resp = []
        for obj in bucket.objects.all():
            resp.append(obj.key)
    except Exception as err:
        logger.exception(f'Error: {err}')
    else:
        return resp
    
    
def read_file(bucket, key, s3):
    try:
        bucket = s3.bucket(bucket)
        obj = bucket.Object(key)
        resp = obj.get()['Body'].read().decode('utf-8')
    except Exception as err:
      logger.exception(f'Error: {err}')
    else:
        return resp
    
    
def write_obj(bucket, key, data, s3):
    
    try:
      obj = s3.Object(bucket, key)
      obj.put(Body=data)
    except Exception as err:
      logger.exception(f'Error: {err}') 
      
      
def append_obj(bucket, key, data, s3):
    old_data = read_file(bucket, key, s3)
    new_data = old_data+'\n'+data
    write_obj(bucket, key, new_data, s3)


def handler(event, context):
    
    region = event['aws_region']
    action = event['task']
    ret = ''
    
    s3_client = boto3.client("s3", region_name=region, 
                             endpoint_url=LOCALSTACK_INTERNAL_ENDPOINT_URL)
    s3_resource = boto3.resource("s3", region_name=region, 
                                 endpoint_url=LOCALSTACK_INTERNAL_ENDPOINT_URL)
    
    bucket = event[action]['bucket_name']
    
    if(action == 'delete_bucket'):
        del_bucket(bucket, s3_client)
    elif(action == 'delete_object'):
        key = event[action]['key']
        del_file(bucket, key, s3_resource)
    elif(action == 'read_object'):
        key = event[action]['key']
        ret = read_file(bucket, key, s3_resource)
    elif(action == 'get_objects'):
        obj_list = list_bucket_contents(bucket, s3_resource)
        for obj in obj_list:
            ret = ret + f's3://{bucket}/{obj}\n'
    elif(action == 'make_object'):
        key = event[action]['key']
        obj = event[action]['object']
        upload_file(key, bucket, s3_client, obj_name=obj)
    elif(action == 'write_object'):
        key = event[action]['key']
        data = event[action]['write_data']
        write_obj(bucket, key, data, s3_resource)
    elif(action == "append_object"):
        key = event[action]['key']
        data = event[action]['write_data']
        append_obj(bucket, key, data, s3_resource)
    elif(action == 'make_bucket'):
        create_bucket(bucket, s3_client)
    else:
        logger.error(f'{action} is an invalid task.')
        
    return ret
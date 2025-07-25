import boto3
from config import Config

AWS_ACCESS_KEY_ID = Config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = Config.AWS_SECRET_ACCESS_KEY

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def upload_file_to_s3(file_object, bucket_name, object_name, acl="private"):
    s3 = boto3.client('s3',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
    s3_client.upload_fileobj(
        file_object, bucket_name, object_name,
        ExtraArgs={
            "ACL": acl,
            "ServerSideEncryption": "AES256"
        }
    )

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    s3 = boto3.client('s3',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
    return s3_client.generate_presigned_url('get_object',
        Params={"Bucket": bucket_name, "Key": object_name},
        ExpiresIn=expiration)

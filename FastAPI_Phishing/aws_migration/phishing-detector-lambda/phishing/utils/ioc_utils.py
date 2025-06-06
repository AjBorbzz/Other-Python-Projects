import os
import boto3
from botocore.exceptions import ClientError

def get_api_key(key_name):
    """
    Get API key from AWS Secrets Manager or environment variables
    """
    # Try AWS Secrets Manager first
    try:
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=key_name.lower().replace('_', '-'))
        return response['SecretString']
    except ClientError:
        pass
    
    # Fallback to environment variables
    return os.environ.get(key_name)
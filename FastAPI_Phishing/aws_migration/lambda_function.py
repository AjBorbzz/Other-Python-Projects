import json
import os
import logging
from phishing.detector import process_phishing_detection

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    try:
        # Parse the incoming event
        if 'body' in event:
            # API Gateway event
            data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation or other event sources
            data = event
        
        logger.info(f"Processing phishing detection for data: {data}")
        
        # Process the phishing detection
        result, original_data = process_phishing_detection(data)
        
        # Return response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'result': result,
                'original_data': original_data,
                'status': 'success'
            })
        }
        
        logger.info("Phishing detection completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing phishing detection: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'status': 'error'
            })
        }
# Sample introduction to AWS Lambda

import json

def lambda_function(event, context):
    print(f"Received event: {json.dumps(event)}")

    name = event.get("name", "World")

    response = {
        "statusCode": 200,
        "body": json.dumps(f"Hello, {name}")s
    }

    return response
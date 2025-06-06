import os
import anthropic
import boto3
from botocore.exceptions import ClientError
from .utils.logging_config import log_duration
from .utils.ioc_utils import get_api_key

# Initialize AWS clients
secrets_client = boto3.client('secretsmanager')

def get_secret(secret_name):
    """
    Retrieve secret from AWS Secrets Manager
    """
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise Exception(f"Error retrieving secret {secret_name}: {str(e)}")

def get_anthropic_client():
    """
    Initialize Anthropic client with API key from AWS Secrets Manager or environment
    """
    try:
        # Try to get from AWS Secrets Manager first
        api_key = get_secret("anthropic-api-key")
    except:
        # Fallback to environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not found in Secrets Manager or environment variables")
    
    return anthropic.Anthropic(api_key=api_key)

# Initialize client
client = get_anthropic_client()

@log_duration
def process_phishing_detection(data):
    """
    Process phishing detection using Claude
    """
    prompt_ = f"""
    Analyze the following data for phishing indicators:
    
    Data: {data}
    
    Please provide a comprehensive security assessment including:
    1. Risk level (Low/Medium/High/Critical)
    2. Specific phishing indicators found
    3. Confidence score (0-100)
    4. Recommended immediate actions
    5. Technical details for security team
    
    Format your response as JSON with the following structure:
    {{
        "risk_level": "Low|Medium|High|Critical",
        "confidence_score": 85,
        "indicators": ["indicator1", "indicator2"],
        "recommendations": ["action1", "action2"],
        "technical_details": "detailed analysis"
    }}
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0.1,  # Low temperature for consistent security analysis
        system="You are an expert Security Automation Engineer specializing in phishing detection and threat analysis. Provide accurate, actionable security assessments.",
        messages=[{"role": "user", "content": prompt_}],
        stream=False,
    )
    
    response = message.content[0].text
    return response, data
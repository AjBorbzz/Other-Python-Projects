from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import anthropic
import json


app = FastAPI()

class PhishingRequest(BaseModel):
    data: dict

class PhishingResponse(BaseModel):
    result: str
    original_data: dict

def get_api_key(key_name):
    return os.environ.get(key_name)

claude_api = get_api_key("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=claude_api)


@app.post("/detect-phishing", response_model=PhishingResponse)
async def detect_phishing(request: PhishingRequest):
    try:
        result, data = process_phishing_detection(request.data)
        return PhishingResponse(result=result, original_data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @log_duration
def process_phishing_detection(data):
    prompt_ = f"""
    Analyze the following data for phishing indicators:
    {data}
    
    Provide a security assessment including:
    1. Risk level (Low/Medium/High)
    2. Key indicators found
    3. Recommended actions
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0.3,  # Lower temperature for consistent security analysis
        system="You are a Security Automation Engineer specializing in phishing detection.",
        messages=[{"role": "user", "content": prompt_}],
        stream=False,
    )
    
    response = message.content[0].text
    return response, data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
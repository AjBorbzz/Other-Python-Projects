from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
from app import PhishingRequest, process_phishing_detection

app = FastAPI(title="Phishing Detection Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/")
async def root():
    return {"message": "Phishing Detection Service", "version": "1.0.0"}

# Background task for processing
async def process_in_background(data: dict):
    # Your processing logic here
    result, _ = process_phishing_detection(data)
    # Store result or send notification
    return result

@app.post("/detect-phishing-async")
async def detect_phishing_async(request: PhishingRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_in_background, request.data)
    return {"message": "Processing started", "status": "accepted"}
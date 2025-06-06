from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import anthropic


app = FastAPI()

class PhishingRequest(BaseModel):
    data: dict

class PhishingResponse(BaseModel):
    result: str
    original_data: dict
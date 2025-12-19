from fastapi import (
    FastAPI, HTTPException, status, Depends, Query, Path, Body, Cookie,
    Header, File, UploadFile, Form, BackgroundTasks, Request
) 
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator 
from typing import Union, Any 
from datetime import datetime, timedelta 
from enum import Enum 
import time 


app = FastAPI(
    title="Complete FastAPI CRUD",
    description="Every feature from official docs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time 
    response.headers["X-Process-Time"] = str(process_time)
    return response
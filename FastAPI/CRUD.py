from fastapi import (
    FastAPI, HTTPException, status, Depends, Query, Path, Body, Cookie,
    Header, File, UploadFile, Form, BackgroundTasks, Request
) 
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator 
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

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Address(BaseModel):
    street: str
    city: str 
    country: str 
    zip_code: str = Field(regex=r"^\d{5}$")

class User(BaseModel):
    username : str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: Union[str, None] = None 
    role: UserRole = UserRole.USER 
    is_active: bool = True 
    created_at: datetime = Field(default_factory=datetime.now)
    address: Union[Address, None] = None 

    @field_validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v 
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "role": "user"
            }
        }

class UserIn(User):
    password: str = Field(min_length=8)

class UserOut(User):
    id: int 

class Item(BaseModel):
    name: str
    description: Union[str, None] = None 
    price: float = Field(gt=0, description="Price must be greater than 0")
    tax: Union[float, None] = Field(default=None, ge=0, le=100)
    tags: list[str] = []
    images: list[HttpUrl] = []

class ItemUpdate(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[float, None] = Field(default=None, gt=0)
    tax: Union[float, None] = None
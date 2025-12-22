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


def common_parameters(
        q: Union[str, None] = Query(default=None, min_length=3),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=100, le=100)
):
    return {"q": q, "skip": skip, "limit": limit}

class Pagination:
    def __init__(self, page: int=Query(1, ge=1), size: int= Query(10, ge=1, le=100)):
        self.page = page
        self.size = size 
        self.skip = (page-1) * size
        
def get_db():
    db = {"connected": True} 
    try: 
        yield db 
    finally:
        db["connected"] = False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "fake-token":
        raise HTTPException(status_code=401, detail = "Invalid token")
    return {"username": "johndoe", "role": "user"}

def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail = "Admin access required")
    return current_user 

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Complete Guide"}

@app.get("/items/{item_id}")
def read_item(
    item_id: int = Path(ge=1, title="Item ID"),
    q: Union[str, None] = Query(default=None, max_length=50),
    commons: dict = Depends(common_parameters)
):
    return {"item_id": item_id, "q": q, **commons}

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return item 

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemUpdate):
    updated_item = {"id": item_id, **item.model_dump(exclude_unset=True)}

@app.patch("/items/{item_id}")
def patch_item(item_id: int, item: ItemUpdate):
    return {"item_id": item_id, "updated_fields": item.model_dump(exclude_unset=True)}

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    return None


@app.put("/items/{item_id}/advanced")
def update_item_advanced(
    item_id: int,
    item: Item,
    user: User,
    importance: int = Body(ge=1, le=5),
    q: Union[str, None] = None
):
    return {"item_id": item_id, "item": item, "user": user, "importance": importance, "q": q}

@app.put("/items/{item_id}/single-body")
def update_with_extra(
    item_id: int,
    item: Item = Body(embed=True),  # {"item": {...}}
):
    return {"item_id": item_id, "item": item}

@app.get("/cookies")
def read_cookies(
    session_id: str | None = Cookie(default=None),
    ads_id: str | None = Cookie(default=None)
):
    return {"session_id": session_id, "ads_id": ads_id}

@app.get("/headers")
def read_headers(
    user_agent: str | None = Header(default=None),
    x_token: str | None = Header(default=None),
    accept_language: str | None = Header(default=None)
):
    return {
        "User-Agent": user_agent,
        "X-Token": x_token,
        "Accept-Language": accept_language
    }

@app.post("/login")
def login(username: str = Form(), password: str = Form()):
    return {"username": username}

@app.post("/files")
async def create_file(
    file: bytes = File(),
    file_b: UploadFile = File(),
    token: str = Form()
):
    return {
        "file_size": len(file),
        "file_b_content_type": file_b.content_type,
        "token": token
    }

@app.post("/uploadfiles")
async def upload_multiple_files(files: list[UploadFile]):
    return [{"filename": f.filename, "content_type": f.content_type} for f in files]


@app.get("/items-error/{item-id}")
def read_item_error(item_id: int):
    if item_id == 0:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Item error header"}
        )
    return {"item_id": item_id}


class CustomException(Exception):
    def __init__(self, name: str):
        self.name = name
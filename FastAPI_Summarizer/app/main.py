from typing import Optional, List 
from enum import Enum

from fastapi import FastAPI, HTTPException, status, Body
from pydantic import BaseModel, Field


app = FastAPI(title="Foundations API", version="0.1.0")

class Flavor(str, Enum):
    vanilla = "vanilla"
    chocolate = "chocolate"
    ube = "ube"

class ItemIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., ge=0)
    tags: List[str] = Field(default_factory=list)
    flavor: Optional[Flavor] = None

class ItemOut(BaseModel):
    id: int
    name: str
    price: float
    tags: List[str]
    flavor: Optional[Flavor]


DB: List[ItemOut] = []
_id = 0

@app.get("/", summary="Health Check")
def root():
    return {"ok": True, "service": "Foundations API"}

@app.get("/items", response_model=List[ItemOut])
def list_items(limit: int=50):
    return DB[:limit]

@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    for it in DB:
        if it.id == item_id:
            return it 
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemIn):
    global _id
    _id += 1 
    item = ItemOut(id=id, **payload.model_dump())
    DB.append(item)
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    idx = next((i for i, it in enumerate(DB) if it.id == item_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Item not found")
    DB.pop(idx)
    return


@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemIn = Body(...)):
    for idx, item in enumerate(DB):
        if item.id == item_id:
            updated = ItemOut(id=item.id, **payload.model_dump())
            DB[idx] = updated
    raise HTTPException(status_code=404, detail="Item not found")
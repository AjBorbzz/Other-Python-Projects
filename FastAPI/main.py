from enum import Enum
from fastapi import FastAPI, Query, Path, Body
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from typing import List, Union

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()

class User(BaseModel):
    username: str
    full_name: str | None = None

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class FilterParams(BaseModel):
    model_config = {"extra", "forbid"}
    limit : int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "Message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "Message": "LeCNN all the images"}
    return {"moel_name": model_name, "Message": "Have some residuals"}

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@app.get("/items/{item_id}")
async def read_items(item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
                     q: str,
                     size: Annotated[float, Query(gt=0, lt = 10.5)]
                    ):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})

    if size:
        results.update({"size": size})
    return results

@app.put("/items/{item_id}")
async def update_item(*,
                    item_id: int, 
                    item: Annotated[Item, Body(embed=True)], 
                    user: User, 
                    importance: Annotated[int, Body(gt=0)],
                    q: str | None = None):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


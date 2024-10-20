from enum import Enum
from fastapi import FastAPI

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "Message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "Message": "LeCNN all the images"}
    return {"moel_name": model_name, "Message": "Have some residuals"}

@app.get("/items/")
async def read_items(skip: int=0, limit: int= 10):
    return fake_items_db[skip : skip + limit]
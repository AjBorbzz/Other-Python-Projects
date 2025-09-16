from datetime import datetime
from enum import Enum 
from typing import List, Optional 
from uuid import UUID 

from pydantic import BaseModel, conint, conlist

class OrderItemSchema(BaseModel):
    product: str
    size: Size 
    quantity: int = Optional[conint(ge=1, strict=True)] = 1
    model_config = {"extra": "forbid"}

class CreateOrderSchema(BaseModel):
    order: List[OrderItemSchema]
    model_config = {"extra": "forbid"}

class GetOrderSchema(CreateOrderSchema):
    id: UUID
    created: datetime
    status: StatusEnum
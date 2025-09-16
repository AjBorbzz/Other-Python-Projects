from datetime import datetime
from enum import Enum
from typing import List, Optional, Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveInt


class Size(str, Enum):
    """Available product sizes"""
    SMALL = "small"
    MEDIUM = "medium" 
    LARGE = "large"
    EXTRA_LARGE = "xl"
    EXTRA_EXTRA_LARGE = "xxl"


class StatusEnum(str, Enum):
    """Order status options"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemSchema(BaseModel):
    """Schema for individual order items"""
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    product: Annotated[str, Field(
        min_length=1,
        max_length=200,
        description="Product name or identifier",
        examples=["Classic T-Shirt", "Premium Hoodie"]
    )]
    
    size: Annotated[Size, Field(
        description="Product size selection"
    )]
    
    quantity: Annotated[PositiveInt, Field(
        default=1,
        le=100,  # Maximum quantity limit
        description="Quantity of items to order",
        examples=[1, 2, 5]
    )]
    
    unit_price: Annotated[Optional[float], Field(
        default=None,
        gt=0,
        description="Unit price of the item (optional for creation)",
        examples=[19.99, 29.95]
    )] = None
    
    @field_validator('product')
    @classmethod
    def validate_product_name(cls, v: str) -> str:
        """Ensure product name is not just whitespace"""
        if not v.strip():
            raise ValueError("Product name cannot be empty or just whitespace")
        return v.strip()


class CreateOrderSchema(BaseModel):
    """Schema for creating new orders"""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    order: Annotated[List[OrderItemSchema], Field(
        min_length=1,
        max_length=50,  # Reasonable order size limit
        description="List of items in the order",
        alias="items"  # Accept both 'order' and 'items' in JSON
    )]
    
    customer_notes: Annotated[Optional[str], Field(
        default=None,
        max_length=500,
        description="Optional customer notes or special instructions"
    )] = None
    
    @field_validator('order')
    @classmethod
    def validate_unique_products(cls, v: List[OrderItemSchema]) -> List[OrderItemSchema]:
        """Ensure no duplicate product-size combinations"""
        seen = set()
        for item in v:
            combo = (item.product.lower(), item.size)
            if combo in seen:
                raise ValueError(f"Duplicate product-size combination: {item.product} ({item.size.value})")
            seen.add(combo)
        return v


class GetOrderSchema(BaseModel):
    """Schema for retrieving order information"""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        # Enable JSON schema generation
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "items": [
                    {
                        "product": "Classic T-Shirt",
                        "size": "medium",
                        "quantity": 2,
                        "unit_price": 19.99
                    }
                ],
                "status": "confirmed",
                "created": "2024-03-15T10:30:00Z",
                "total_amount": 39.98,
                "customer_notes": "Please deliver after 3 PM"
            }
        }
    )
    
    id: Annotated[UUID, Field(
        description="Unique order identifier",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )]
    
    items: Annotated[List[OrderItemSchema], Field(
        description="List of ordered items"
    )]
    
    status: Annotated[StatusEnum, Field(
        description="Current order status"
    )]
    
    created: Annotated[datetime, Field(
        description="Order creation timestamp"
    )]
    
    total_amount: Annotated[Optional[float], Field(
        default=None,
        ge=0,
        description="Total order amount in currency units"
    )] = None
    
    customer_notes: Annotated[Optional[str], Field(
        default=None,
        description="Customer notes or special instructions"
    )] = None


class UpdateOrderStatusSchema(BaseModel):
    """Schema for updating order status"""
    model_config = ConfigDict(extra="forbid")
    
    status: Annotated[StatusEnum, Field(
        description="New status for the order"
    )]
    
    notes: Annotated[Optional[str], Field(
        default=None,
        max_length=500,
        description="Optional notes about the status change"
    )] = None


class OrderSummarySchema(BaseModel):
    """Lightweight schema for order summaries/lists"""
    model_config = ConfigDict(extra="forbid")
    
    id: UUID
    status: StatusEnum
    created: datetime
    item_count: Annotated[PositiveInt, Field(
        description="Total number of items in the order"
    )]
    total_amount: Annotated[Optional[float], Field(
        default=None,
        ge=0,
        description="Total order value"
    )] = None


# Response schemas for API documentation
class OrderResponse(BaseModel):
    """Standard API response wrapper for orders"""
    model_config = ConfigDict(extra="forbid")
    
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[GetOrderSchema] = None


class OrderListResponse(BaseModel):
    """Response schema for paginated order lists"""
    model_config = ConfigDict(extra="forbid")
    
    success: bool = True
    message: str = "Orders retrieved successfully"
    data: List[OrderSummarySchema] = []
    total: int = 0
    page: int = 1
    per_page: int = 10
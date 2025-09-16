from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Query, Path, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from orders.app import app
from orders.schema import (
    CreateOrderSchema, 
    GetOrderSchema, 
    UpdateOrderStatusSchema,
    OrderSummarySchema,
    OrderResponse,
    OrderListResponse,
    StatusEnum
)

# In-memory storage (replace with database in production)
orders_db: Dict[str, Dict[str, Any]] = {}

# Sample data for demonstration
SAMPLE_ORDER = {
    'id': uuid4(),
    'status': StatusEnum.DELIVERED,
    'created': datetime.now(timezone.utc),
    'items': [
        {
            'product': 'Cappuccino',
            'size': 'medium',
            'quantity': 1,
            'unit_price': 4.50
        }
    ],
    'total_amount': 4.50,
    'customer_notes': 'Extra foam please'
}

# Initialize with sample data
orders_db[str(SAMPLE_ORDER['id'])] = SAMPLE_ORDER


# Dependency for order validation
async def get_order_or_404(
    order_id: UUID = Path(
        ..., 
        description="Unique order identifier",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
) -> Dict[str, Any]:
    """Retrieve order by ID or raise 404 if not found"""
    order = orders_db.get(str(order_id))
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return order


@app.get(
    '/orders',
    response_model=OrderListResponse,
    summary="Get all orders",
    description="Retrieve a paginated list of all orders with optional filtering",
    tags=["Orders"]
)
async def get_orders(
    status_filter: Optional[StatusEnum] = Query(
        None, 
        description="Filter orders by status"
    ),
    page: int = Query(
        1, 
        ge=1, 
        description="Page number for pagination"
    ),
    per_page: int = Query(
        10, 
        ge=1, 
        le=100, 
        description="Number of orders per page"
    )
) -> OrderListResponse:
    """Get all orders with pagination and filtering"""
    try:
        # Filter orders by status if provided
        filtered_orders = []
        for order_data in orders_db.values():
            if status_filter is None or order_data['status'] == status_filter:
                # Convert to summary format
                summary = OrderSummarySchema(
                    id=order_data['id'],
                    status=order_data['status'],
                    created=order_data['created'],
                    item_count=len(order_data['items']),
                    total_amount=order_data.get('total_amount')
                )
                filtered_orders.append(summary)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_orders = filtered_orders[start_idx:end_idx]
        
        return OrderListResponse(
            data=paginated_orders,
            total=len(filtered_orders),
            page=page,
            per_page=per_page,
            message=f"Retrieved {len(paginated_orders)} orders (page {page} of {(len(filtered_orders) - 1) // per_page + 1})"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve orders: {str(e)}"
        )


@app.post(
    '/orders', 
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse,
    summary="Create new order",
    description="Create a new order with the provided items",
    tags=["Orders"]
)
async def create_order(order_data: CreateOrderSchema) -> OrderResponse:
    """Create a new order"""
    try:
        # Generate new order
        order_id = uuid4()
        
        # Calculate total amount
        total_amount = sum(
            item.quantity * (item.unit_price or 0) 
            for item in order_data.order
        ) if any(item.unit_price for item in order_data.order) else None
        
        new_order = {
            'id': order_id,
            'status': StatusEnum.PENDING,
            'created': datetime.now(timezone.utc),
            'items': [item.model_dump() for item in order_data.order],
            'total_amount': total_amount,
            'customer_notes': order_data.customer_notes
        }
        
        # Store in database
        orders_db[str(order_id)] = new_order
        
        # Convert to response schema
        response_order = GetOrderSchema(**new_order)
        
        return OrderResponse(
            message=f"Order created successfully with ID: {order_id}",
            data=response_order
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e.errors()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@app.get(
    '/orders/{order_id}',
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve detailed information about a specific order",
    tags=["Orders"]
)
async def get_order(
    order: Dict[str, Any] = Depends(get_order_or_404)
) -> OrderResponse:
    """Get a specific order by ID"""
    try:
        response_order = GetOrderSchema(**order)
        return OrderResponse(
            message="Order retrieved successfully",
            data=response_order
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve order: {str(e)}"
        )


@app.put(
    '/orders/{order_id}',
    response_model=OrderResponse,
    summary="Update order",
    description="Update an existing order (only allowed for pending orders)",
    tags=["Orders"]
)
async def update_order(
    order_data: CreateOrderSchema,
    order: Dict[str, Any] = Depends(get_order_or_404)
) -> OrderResponse:
    """Update an existing order"""
    try:
        # Check if order can be updated
        if order['status'] not in [StatusEnum.PENDING, StatusEnum.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update order with status: {order['status'].value}"
            )
        
        # Calculate new total amount
        total_amount = sum(
            item.quantity * (item.unit_price or 0) 
            for item in order_data.order
        ) if any(item.unit_price for item in order_data.order) else order.get('total_amount')
        
        # Update order
        order.update({
            'items': [item.model_dump() for item in order_data.order],
            'total_amount': total_amount,
            'customer_notes': order_data.customer_notes
        })
        
        response_order = GetOrderSchema(**order)
        
        return OrderResponse(
            message="Order updated successfully",
            data=response_order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order: {str(e)}"
        )


@app.delete(
    '/orders/{order_id}', 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete order",
    description="Delete an order (only allowed for pending orders)",
    tags=["Orders"]
)
async def delete_order(
    order: Dict[str, Any] = Depends(get_order_or_404)
) -> None:
    """Delete an order"""
    try:
        # Check if order can be deleted
        if order['status'] != StatusEnum.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete order with status: {order['status'].value}. Only pending orders can be deleted."
            )
        
        # Delete order
        del orders_db[str(order['id'])]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete order: {str(e)}"
        )


@app.post(
    '/orders/{order_id}/cancel',
    response_model=OrderResponse,
    summary="Cancel order",
    description="Cancel an existing order (if cancellation is allowed)",
    tags=["Order Actions"]
)
async def cancel_order(
    reason: Optional[str] = Query(
        None, 
        description="Reason for cancellation",
        max_length=500
    ),
    order: Dict[str, Any] = Depends(get_order_or_404)
) -> OrderResponse:
    """Cancel an order"""
    try:
        # Check if order can be cancelled
        if order['status'] in [StatusEnum.DELIVERED, StatusEnum.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status: {order['status'].value}"
            )
        
        # Update order status
        order['status'] = StatusEnum.CANCELLED
        if reason:
            order['customer_notes'] = f"{order.get('customer_notes', '')} | Cancellation reason: {reason}".strip('| ')
        
        response_order = GetOrderSchema(**order)
        
        return OrderResponse(
            message="Order cancelled successfully",
            data=response_order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}"
        )


@app.post(
    '/orders/{order_id}/pay',
    response_model=OrderResponse,
    summary="Process payment",
    description="Process payment for an order and update status",
    tags=["Order Actions"]
)
async def pay_order(
    payment_method: str = Query(
        ..., 
        description="Payment method used",
        example="credit_card"
    ),
    order: Dict[str, Any] = Depends(get_order_or_404)
) -> OrderResponse:
    """Process payment for an order"""
    try:
        # Check if order can be paid
        if order['status'] not in [StatusEnum.PENDING, StatusEnum.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot process payment for order with status: {order['status'].value}"
            )
        
        # Simulate payment processing
        if not order.get('total_amount'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot process payment: order total amount not set"
            )
        
        # Update order status after successful payment
        order['status'] = StatusEnum.CONFIRMED
        
        # Add payment info to notes
        payment_note = f"Payment processed via {payment_method} on {datetime.now(timezone.utc).isoformat()}"
        order['customer_notes'] = f"{order.get('customer_notes', '')} | {payment_note}".strip('| ')
        
        response_order = GetOrderSchema(**order)
        
        return OrderResponse(
            message=f"Payment processed successfully via {payment_method}",
            data=response_order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment: {str(e)}"
        )


@app.patch(
    '/orders/{order_id}/status',
    response_model=OrderResponse,
    summary="Update order status",
    description="Update the status of an existing order",
    tags=["Order Actions"]
)
async def update_order_status(
    status_update: UpdateOrderStatusSchema,
    order: Dict[str, Any] = Depends(get_order_or_404)
) -> OrderResponse:
    """Update order status"""
    try:
        # Validate status transition (business logic)
        current_status = order['status']
        new_status = status_update.status
        
        # Define valid status transitions
        valid_transitions = {
            StatusEnum.PENDING: [StatusEnum.CONFIRMED, StatusEnum.CANCELLED],
            StatusEnum.CONFIRMED: [StatusEnum.PREPARING, StatusEnum.CANCELLED],
            StatusEnum.PREPARING: [StatusEnum.SHIPPED, StatusEnum.CANCELLED],
            StatusEnum.SHIPPED: [StatusEnum.DELIVERED],
            StatusEnum.DELIVERED: [],  # Final state
            StatusEnum.CANCELLED: []   # Final state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status.value} to {new_status.value}"
            )
        
        # Update status
        order['status'] = new_status
        if status_update.notes:
            status_note = f"Status changed to {new_status.value}: {status_update.notes}"
            order['customer_notes'] = f"{order.get('customer_notes', '')} | {status_note}".strip('| ')
        
        response_order = GetOrderSchema(**order)
        
        return OrderResponse(
            message=f"Order status updated to {new_status.value}",
            data=response_order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(e)}"
        )


# Health check endpoint
@app.get(
    '/orders/health',
    summary="Health check",
    description="Check if the orders service is running",
    tags=["System"]
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "orders_count": len(orders_db)
    }
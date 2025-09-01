from datetime import datetime
from uuid import UUID 
from starlette.responses import Response 
from starlette import status


from orders.app import app 

orders = []

# sample payload
order = {
    'id': 'e0b8ce39-d12c-4dad-9fb6-f6743bd674f4',
    'status': 'delivered',
    'created': datetime.now(datetime.timezone.utc),
    'order': [
        {
            'product': 'cappuccino',
            'size': 'medium',
            'quantity': 1
        }
    ]
}

@app.get('/orders')
def get_orders():
    return {'orders': [orders]}

@app.post('/orders', status_code=status.HTTP_201_CREATED)
def create_order():
    return order  

@app.get('/orders/{order_id}')
def get_order(order_id: UUID):
    return order 

@app.put('/orders/{order_id}')
def update_order(order_id: UUID):
    return order 

@app.delete('/orders/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: UUID):
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post('/orders/{order_id}/cancel')
def cancel_order(order_id: UUID):
    return order 

@app.post('/orders/{order_id}/pay')
def pay_order(order_id: UUID):
    return order
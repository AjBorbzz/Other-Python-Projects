from datetime import datetime
from uuid import UUID 
from starlette.responses import Response 
from starlette import status


from orders.app import app 

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
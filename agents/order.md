# OrderAgent

```yaml
name: OrderAgent
version: 1.0.0
description: Processes customer orders with status tracking
storage: memory
statuses:
  - pending
  - confirmed
  - preparing
  - shipped
  - delivered
  - cancelled
```

## Overview

OrderAgent handles all order-related operations including order creation, status tracking, cancellation, and order history retrieval. It maintains an in-memory store of all orders.

## Capabilities

- Create new orders from cart items
- Track order status through lifecycle
- Get order history
- Get orders by user
- Get specific order by ID
- Update order status
- Cancel orders

## Order Statuses

| Status | Description |
|--------|-------------|
| pending | Order placed, awaiting confirmation |
| confirmed | Order confirmed by system |
| preparing | Order being prepared for delivery |
| shipped | Order dispatched for delivery |
| delivered | Order delivered to customer |
| cancelled | Order cancelled |

## Methods

### place_order(items, total, address, user_id=None)

Creates a new order from cart items.

```python
def place_order(self, items: List[Dict], total: float, 
                address: str = "", user_id: int = None) -> Dict:
    order = Order(
        order_id=self._next_id,
        items=items,
        total=total,
        address=address,
        user_id=user_id
    )
    self._orders[self._next_id] = order
    self._next_id += 1
    return order.to_dict()
```

**Parameters:**
- `items` (List[Dict]) - List of cart items
- `total` (float) - Order total amount
- `address` (str) - Delivery address
- `user_id` (int, optional) - User identifier

**Returns:** Created order dict

---

### get_order_history()

Returns all orders in the system.

```python
def get_order_history(self) -> List[Dict]:
    return [o.to_dict() for o in self._orders.values()]
```

**Returns:** List of all orders

---

### get_user_orders(user_id: int)

Gets all orders for a specific user.

```python
def get_user_orders(self, user_id: int) -> List[Dict]:
    return [o.to_dict() for o in self._orders.values() 
            if o.user_id == user_id]
```

**Parameters:**
- `user_id` (int) - User identifier

**Returns:** List of user's orders

---

### get_order_by_id(order_id: int)

Gets a specific order by ID.

```python
def get_order_by_id(self, order_id: int) -> Optional[Dict]:
    if order_id in self._orders:
        return self._orders[order_id].to_dict()
    return None
```

**Parameters:**
- `order_id` (int) - Order identifier

**Returns:** Order dict or None

---

### update_status(order_id: int, status: str)

Updates the status of an order.

```python
def update_status(self, order_id: int, status: str) -> bool:
    if order_id in self._orders:
        self._orders[order_id].status = status
        return True
    return False
```

**Parameters:**
- `order_id` (int) - Order identifier
- `status` (str) - New status

**Returns:** True if updated, False if not found

---

### cancel_order(order_id: int)

Cancels an order.

```python
def cancel_order(self, order_id: int) -> bool:
    if order_id in self._orders:
        self._orders[order_id].status = "cancelled"
        return True
    return False
```

**Parameters:**
- `order_id` (int) - Order identifier

**Returns:** True if cancelled, False if not found

---

## Data Structures

### Order

```python
class Order:
    id: int
    user_id: int
    items: List[Dict]
    total: float
    address: str
    status: str
    created_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": self.items,
            "total": self.total,
            "address": self.address,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
```

### Order Item

```python
{
    "product_id": int,
    "name": str,
    "price": float,
    "quantity": int,
    "unit": str,
    "subtotal": float
}
```

## Usage Example

```python
from agents import get_order_agent

orders = get_order_agent()

# Create order
order = orders.place_order(
    items=[
        {"product_id": 1, "name": "Tomatoes", "price": 3.99, "quantity": 2}
    ],
    total=11.97,
    address="123 Main St",
    user_id=1
)
print(f"Order #{order['id']} created")

# Get user orders
my_orders = orders.get_user_orders(1)

# Update status
orders.update_status(1, "preparing")

# Cancel order
orders.cancel_order(1)

# Get order history
all_orders = orders.get_order_history()
```

## Workflow Integration

OrderAgent is used in the `order_placement` workflow:

1. CartAgent validates cart items
2. OrderAgent creates order with status "confirmed"
3. NotificationAgent sends order confirmation

## Events

| Event | Trigger | Action |
|-------|---------|--------|
| order_created | place_order() | Set status to "confirmed" |
| order_cancelled | cancel_order() | Set status to "cancelled" |
| order_updated | update_status() | Update status field |

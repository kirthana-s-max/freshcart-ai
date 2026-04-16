# CartAgent

```yaml
name: CartAgent
version: 1.0.0
description: Handles shopping cart operations with in-memory storage
storage: memory
delivery_fee: 2.99
max_items: 50
```

## Overview

CartAgent manages the shopping cart functionality, allowing users to add, remove, and update items. It calculates totals including delivery fees and provides cart persistence capabilities.

## Capabilities

- Add items to cart
- Remove items from cart
- Update item quantities
- Calculate totals with delivery fee
- View cart contents
- Clear cart
- Get cart count
- Persist cart to localStorage (frontend integration)

## Methods

### add_item(product_id, name, price, quantity, unit)

Adds an item to the cart or increases quantity if it already exists.

```python
def add_item(self, product_id: int, name: str, price: float, 
             quantity: int = 1, unit: str = "") -> Dict:
    if product_id in self._cart:
        self._cart[product_id].quantity += quantity
    else:
        self._cart[product_id] = CartItem(product_id, name, price, quantity, unit)
    return self._cart[product_id].to_dict()
```

**Parameters:**
- `product_id` (int) - Product identifier
- `name` (str) - Product name
- `price` (float) - Price per unit
- `quantity` (int) - Quantity to add (default: 1)
- `unit` (str) - Unit of measurement

**Returns:** Updated cart item dict

---

### remove_item(product_id: int)

Removes an item from the cart.

```python
def remove_item(self, product_id: int) -> bool:
    if product_id in self._cart:
        del self._cart[product_id]
        return True
    return False
```

**Parameters:**
- `product_id` (int) - Product identifier

**Returns:** True if removed, False if not found

---

### update_quantity(product_id: int, quantity: int)

Updates the quantity of an item in the cart.

```python
def update_quantity(self, product_id: int, quantity: int) -> Optional[Dict]:
    if product_id not in self._cart:
        return None
    if quantity <= 0:
        return self.remove_item(product_id)
    self._cart[product_id].quantity = quantity
    return self._cart[product_id].to_dict()
```

**Parameters:**
- `product_id` (int) - Product identifier
- `quantity` (int) - New quantity (0 removes item)

**Returns:** Updated item dict or None if not found

---

### view_cart()

Returns all items in the cart.

```python
def view_cart(self) -> List[Dict]:
    return [item.to_dict() for item in self._cart.values()]
```

**Returns:** List of cart items

---

### calculate_total()

Calculates subtotal, delivery fee, and total.

```python
def calculate_total(self) -> Dict:
    items = self.view_cart()
    subtotal = sum(item['subtotal'] for item in items)
    delivery_fee = self.DELIVERY_FEE if items else 0
    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "total": round(subtotal + delivery_fee, 2)
    }
```

**Returns:** Dict with subtotal, delivery_fee, and total

---

### clear_cart()

Empties the entire cart.

```python
def clear_cart(self):
    self._cart.clear()
```

**Returns:** None

---

### get_cart_count()

Gets the total number of items in the cart.

```python
def get_cart_count(self) -> int:
    return sum(item.quantity for item in self._cart.values())
```

**Returns:** Total item count

---

### is_empty()

Checks if the cart is empty.

```python
def is_empty(self) -> bool:
    return len(self._cart) == 0
```

**Returns:** True if cart is empty

---

## Data Structures

### CartItem

```python
class CartItem:
    product_id: int
    name: str
    price: float
    quantity: int
    unit: str
    
    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "unit": self.unit,
            "subtotal": self.price * self.quantity
        }
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| DELIVERY_FEE | 2.99 | Fixed delivery fee |
| MAX_ITEMS | 50 | Maximum items in cart |

## Usage Example

```python
from agents import get_cart_agent

cart = get_cart_agent()

# Add items
cart.add_item(1, "Organic Tomatoes", 3.99, 2, "kg")
cart.add_item(7, "Red Apples", 4.99, 1, "kg")

# Update quantity
cart.update_quantity(1, 3)

# View cart
items = cart.view_cart()

# Calculate total
totals = cart.calculate_total()
print(f"Total: ${totals['total']}")

# Remove item
cart.remove_item(7)

# Clear cart
cart.clear_cart()
```

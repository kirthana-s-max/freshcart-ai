from typing import List, Dict, Optional
from datetime import datetime

class OrderItem:
    def __init__(self, product_id: int, name: str, price: float, quantity: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.price * self.quantity
        }

class Order:
    def __init__(self, order_id: int, items: List[Dict], total: float):
        self.id = order_id
        self.items = [OrderItem(**item) for item in items]
        self.total = total
        self.created_at = datetime.now()
        self.status = "confirmed"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }

class OrderAgent:
    def __init__(self):
        self._orders: Dict[int, Order] = {}
        self._next_id = 1

    def place_order(self, items: List[Dict], total: float) -> Dict:
        order = Order(order_id=self._next_id, items=items, total=total)
        self._orders[self._next_id] = order
        self._next_id += 1
        return order.to_dict()

    def get_order_history(self) -> List[Dict]:
        return [order.to_dict() for order in self._orders.values()]

    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        if order_id in self._orders:
            return self._orders[order_id].to_dict()
        return None

    def cancel_order(self, order_id: int) -> bool:
        if order_id in self._orders:
            self._orders[order_id].status = "cancelled"
            return True
        return False

order_agent = OrderAgent()

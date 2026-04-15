from typing import List, Dict, Optional
from datetime import datetime

class CartItem:
    def __init__(self, product_id: int, name: str, price: float, quantity: int, unit: str):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.unit = unit

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "unit": self.unit,
            "subtotal": self.price * self.quantity
        }

class CartAgent:
    def __init__(self):
        self._cart: Dict[int, CartItem] = {}

    def add_item(self, product_id: int, name: str, price: float, quantity: int = 1, unit: str = "") -> Dict:
        if product_id in self._cart:
            self._cart[product_id].quantity += quantity
        else:
            self._cart[product_id] = CartItem(product_id, name, price, quantity, unit)
        return self._cart[product_id].to_dict()

    def remove_item(self, product_id: int) -> bool:
        if product_id in self._cart:
            del self._cart[product_id]
            return True
        return False

    def view_cart(self) -> List[Dict]:
        return [item.to_dict() for item in self._cart.values()]

    def calculate_total(self) -> Dict:
        items = self.view_cart()
        subtotal = sum(item['subtotal'] for item in items)
        delivery_fee = 2.99 if items else 0
        total = subtotal + delivery_fee
        return {
            "items": items,
            "subtotal": round(subtotal, 2),
            "delivery_fee": delivery_fee,
            "total": round(total, 2)
        }

    def clear_cart(self):
        self._cart.clear()

    def get_cart_count(self) -> int:
        return sum(item.quantity for item in self._cart.values())

cart_agent = CartAgent()

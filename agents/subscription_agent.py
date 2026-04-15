from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class SubscriptionFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Subscription:
    def __init__(self, subscription_id: int, product_id: int, product_name: str, 
                 frequency: str, quantity: int, price: float):
        self.id = subscription_id
        self.product_id = product_id
        self.product_name = product_name
        self.frequency = frequency
        self.quantity = quantity
        self.price = price
        self.created_at = datetime.now()
        self.active = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "frequency": self.frequency,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at.isoformat(),
            "active": self.active
        }

class SubscriptionAgent:
    def __init__(self):
        self._subscriptions: Dict[int, Subscription] = {}
        self._next_id = 1

    def create_subscription(self, product_id: int, product_name: str, 
                           frequency: str, quantity: int, price: float) -> Dict:
        valid_frequencies = [f.value for f in SubscriptionFrequency]
        if frequency.lower() not in valid_frequencies:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
        
        subscription = Subscription(
            subscription_id=self._next_id,
            product_id=product_id,
            product_name=product_name,
            frequency=frequency.lower(),
            quantity=quantity,
            price=price
        )
        self._subscriptions[self._next_id] = subscription
        self._next_id += 1
        return subscription.to_dict()

    def get_active_subscriptions(self) -> List[Dict]:
        return [
            sub.to_dict() for sub in self._subscriptions.values() 
            if sub.active
        ]

    def get_all_subscriptions(self) -> List[Dict]:
        return [sub.to_dict() for sub in self._subscriptions.values()]

    def cancel_subscription(self, subscription_id: int) -> bool:
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].active = False
            return True
        return False

    def get_subscription_by_id(self, subscription_id: int) -> Optional[Dict]:
        if subscription_id in self._subscriptions:
            return self._subscriptions[subscription_id].to_dict()
        return None

subscription_agent = SubscriptionAgent()

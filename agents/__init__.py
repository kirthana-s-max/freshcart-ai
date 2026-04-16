"""
FreshCart AI - Multi-Agent System
================================
Markdown-based multi-agent orchestration system.
All agent definitions are in agents.md
"""

from .orchestrator import (
    AgentOrchestrator,
    orchestrator,
    get_product_agent,
    get_cart_agent,
    get_order_agent,
    get_subscription_agent,
    get_notification_agent,
    get_recommendation_agent,
    ProductAgent,
    CartAgent,
    OrderAgent,
    SubscriptionAgent,
    NotificationAgent,
    RecommendationAgent,
    BaseAgent,
    AgentDefinition,
)

__all__ = [
    "AgentOrchestrator",
    "orchestrator",
    "get_product_agent",
    "get_cart_agent",
    "get_order_agent",
    "get_subscription_agent",
    "get_notification_agent",
    "get_recommendation_agent",
    "ProductAgent",
    "CartAgent",
    "OrderAgent",
    "SubscriptionAgent",
    "NotificationAgent",
    "RecommendationAgent",
    "BaseAgent",
    "AgentDefinition",
]

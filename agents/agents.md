# FreshCart AI - Multi-Agent System

## Agent Definitions

This document serves as an index for all agent definitions. Individual agents are defined in separate markdown files for better organization and maintainability.

## Agent Files

| Agent | File | Purpose |
|-------|------|---------|
| ProductAgent | [product.md](product.md) | Product catalog management |
| CartAgent | [cart.md](cart.md) | Shopping cart operations |
| OrderAgent | [order.md](order.md) | Order processing |
| SubscriptionAgent | [subscription.md](subscription.md) | Subscription management |
| NotificationAgent | [notification.md](notification.md) | User notifications |
| RecommendationAgent | [recommendation.md](recommendation.md) | Product recommendations |
| Orchestrator | [orchestrator.md](orchestrator.md) | Agent orchestration |

## Quick Reference

### Agent Initialization

```python
from agents import orchestrator

# Get orchestrator
orch = orchestrator

# List agents
agents = orch.list_agents()

# Get specific agent
product = orch.get_agent("ProductAgent")

# Execute workflow
result = orch.execute_workflow("order_placement", context)
```

### Convenience Functions

```python
from agents import (
    get_product_agent,
    get_cart_agent,
    get_order_agent,
    get_subscription_agent,
    get_notification_agent,
    get_recommendation_agent
)

# Direct agent access
product = get_product_agent()
cart = get_cart_agent()
order = get_order_agent()
subscription = get_subscription_agent()
notification = get_notification_agent()
recommendation = get_recommendation_agent()
```

## Workflows

| Workflow | Agents | Description |
|----------|--------|-------------|
| order_placement | CartAgent → OrderAgent → NotificationAgent | Full order flow |
| product_discovery | ProductAgent → RecommendationAgent | Search and recommend |
| subscription_management | SubscriptionAgent → NotificationAgent | Manage subscriptions |
| delivery_tracking | OrderAgent → NotificationAgent | Track deliveries |
| cart_recommendation | CartAgent → RecommendationAgent | Cart suggestions |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FreshCart AI                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              AgentOrchestrator                        │  │
│   │  (orchestrator.py - parses agents.md)               │  │
│   └─────────────────────────────────────────────────────┘  │
│                             │                               │
│     ┌───────────┬───────────┼───────────┬───────────┐     │
│     ▼           ▼           ▼           ▼           ▼     │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐  ┌────────┐  │
│  │Product│  │ Cart │  │Order │  │Subscription│  │Notify │  │
│  │Agent │  │Agent │  │Agent │  │   Agent    │  │Agent  │  │
│  └──────┘  └──────┘  └──────┘  └────────────┘  └────────┘  │
│                                                     │       │
│                                                     ▼       │
│                                              ┌───────────┐   │
│                                              │  Recommend│   │
│                                              │   Agent   │   │
│                                              └───────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### Order Placement Flow

```
User Action: Place Order
        │
        ▼
┌─────────────────┐
│   CartAgent     │ ← Validates cart items
│ get_total()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   OrderAgent    │ ← Creates order
│ place_order()   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  NotificationAgent  │ ← Sends confirmation
│ create_order_notif()│
└─────────────────────┘
```

### Product Discovery Flow

```
User Action: Search Product
        │
        ▼
┌─────────────────┐
│  ProductAgent   │ ← Searches products
│ search_products()│
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ RecommendationAgent │ ← Gets similar items
│ recommend_similar() │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ RecommendationAgent │ ← Gets complementary
│ get_complementary()│
└─────────────────────┘
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AGENTS_MD_PATH | agents/agents.md | Path to agent definitions |
| PRODUCTS_CSV_PATH | data/products.csv | Path to products data |

## See Also

- [product.md](product.md) - ProductAgent documentation
- [cart.md](cart.md) - CartAgent documentation
- [order.md](order.md) - OrderAgent documentation
- [subscription.md](subscription.md) - SubscriptionAgent documentation
- [notification.md](notification.md) - NotificationAgent documentation
- [recommendation.md](recommendation.md) - RecommendationAgent documentation
- [orchestrator.md](orchestrator.md) - Orchestrator documentation

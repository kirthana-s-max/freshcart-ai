# Agent Orchestrator

```yaml
name: FreshCartOrchestrator
version: 1.0.0
description: Orchestrates all agents defined in agents.md for coordinated task execution
storage: none
agent_source: agents/agents.md
```

## Overview

The AgentOrchestrator manages and coordinates all agents in the FreshCart AI system. It parses agent definitions from markdown files and provides a unified interface for executing multi-agent workflows.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AgentOrchestrator                          │
├─────────────────────────────────────────────────────────────┤
│  Parses: agents.md                                          │
│  Manages: All agent instances                               │
│  Executes: Workflows                                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  ProductAgent │  │   CartAgent   │  │  OrderAgent   │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│  SubscriptionAgent  │  NotificationAgent                  │
└───────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │RecommendationAgent│
                   └──────────────────┘
```

## Agents

| Agent | Purpose | Dependencies |
|-------|---------|--------------|
| ProductAgent | Product catalog management | None |
| CartAgent | Shopping cart operations | None |
| OrderAgent | Order processing | CartAgent |
| SubscriptionAgent | Subscription management | None |
| NotificationAgent | User notifications | OrderAgent, SubscriptionAgent |
| RecommendationAgent | Product recommendations | ProductAgent |

## Workflows

### order_placement

Handles the complete order flow from cart to confirmation.

```yaml
workflow:
  name: order_placement
  agents:
    - CartAgent
    - OrderAgent
    - NotificationAgent
  steps:
    - agent: CartAgent
      action: validate_cart
      description: Verify cart items are available
    - agent: OrderAgent
      action: place_order
      description: Create order with cart items
    - agent: NotificationAgent
      action: create_order_notification
      description: Send order confirmation
```

**Flow:**
1. Validate cart items
2. Calculate total
3. Create order
4. Send notification
5. Clear cart

---

### product_discovery

Handles product search and recommendation flow.

```yaml
workflow:
  name: product_discovery
  agents:
    - ProductAgent
    - RecommendationAgent
  steps:
    - agent: ProductAgent
      action: search_products
      description: Search products by keyword
    - agent: RecommendationAgent
      action: recommend_similar
      description: Suggest similar products
    - agent: RecommendationAgent
      action: get_complementary
      description: Suggest complementary products
```

**Flow:**
1. Search products
2. Get similar products
3. Get complementary products
4. Return combined results

---

### subscription_management

Handles subscription creation and management.

```yaml
workflow:
  name: subscription_management
  agents:
    - SubscriptionAgent
    - NotificationAgent
  steps:
    - agent: SubscriptionAgent
      action: validate_subscription
      description: Validate subscription parameters
    - agent: SubscriptionAgent
      action: create_subscription
      description: Create subscription
    - agent: NotificationAgent
      action: create_subscription_notification
      description: Send confirmation
```

**Flow:**
1. Validate subscription
2. Calculate next delivery
3. Create subscription
4. Send notification

---

### delivery_tracking

Handles order delivery status updates.

```yaml
workflow:
  name: delivery_tracking
  agents:
    - OrderAgent
    - NotificationAgent
  steps:
    - agent: OrderAgent
      action: update_status
      description: Update delivery status
    - agent: NotificationAgent
      action: create_delivery_notification
      description: Send status update
```

---

### cart_recommendation

Provides cart-based product suggestions.

```yaml
workflow:
  name: cart_recommendation
  agents:
    - CartAgent
    - RecommendationAgent
  steps:
    - agent: CartAgent
      action: view_cart
      description: Get current cart items
    - agent: RecommendationAgent
      action: get_bundle_suggestions
      description: Suggest products to complete bundle
```

## Methods

### orchestrator.list_agents()

Lists all available agents.

```python
def list_agents(self) -> List[str]:
    return list(self.agents.keys())
```

**Returns:** List of agent names

---

### orchestrator.get_agent(name: str)

Gets an agent instance by name.

```python
def get_agent(self, name: str) -> Optional[BaseAgent]:
    return self.agents.get(name)
```

**Parameters:**
- `name` (str) - Agent name

**Returns:** Agent instance or None

---

### orchestrator.execute_workflow(workflow_name: str, context: Dict = None)

Executes a predefined workflow.

```python
def execute_workflow(self, workflow_name: str, context: Dict = None) -> Dict:
    context = context or {}
    results = []
    
    for agent_name in self.workflows[workflow_name]:
        agent = self.get_agent(agent_name)
        results.append({
            "agent": agent_name,
            "status": "executed"
        })
    
    return {"workflow": workflow_name, "results": results, "context": context}
```

**Parameters:**
- `workflow_name` (str) - Name of workflow to execute
- `context` (dict, optional) - Workflow context data

**Returns:** Workflow execution results

**Raises:** ValueError if workflow not found

---

### orchestrator.list_workflows()

Lists all available workflows.

```python
def list_workflows(self) -> List[str]:
    return list(self.workflows.keys())
```

**Returns:** List of workflow names

---

### orchestrator.register_agent(agent: BaseAgent)

Registers a new agent with the orchestrator.

```python
def register_agent(self, agent: BaseAgent):
    self.agents[agent.name] = agent
```

**Parameters:**
- `agent` (BaseAgent) - Agent instance to register

---

### orchestrator.register_workflow(name: str, agent_sequence: List[str])

Registers a new workflow.

```python
def register_workflow(self, name: str, agent_sequence: List[str]):
    self.workflows[name] = agent_sequence
```

**Parameters:**
- `name` (str) - Workflow name
- `agent_sequence` (List[str]) - List of agent names in execution order

## Usage Example

```python
from agents import orchestrator, get_product_agent

# List all agents
agents = orchestrator.list_agents()
print(f"Available agents: {agents}")

# List all workflows
workflows = orchestrator.list_workflows()
print(f"Available workflows: {workflows}")

# Get specific agent
product_agent = orchestrator.get_agent("ProductAgent")

# Execute workflow
result = orchestrator.execute_workflow("order_placement", {
    "user_id": 1,
    "items": [...],
    "address": "123 Main St"
})
print(f"Workflow result: {result}")

# Register custom workflow
orchestrator.register_workflow("custom_workflow", [
    "ProductAgent",
    "RecommendationAgent"
])

# Execute custom workflow
result = orchestrator.execute_workflow("custom_workflow")
```

## Workflow Execution Context

Context data is passed through the workflow chain:

```python
# Example workflow execution
context = {
    "user_id": 1,
    "order_id": None,      # Set by OrderAgent
    "notification_id": None  # Set by NotificationAgent
}

result = orchestrator.execute_workflow("order_placement", context)

# Result structure
{
    "workflow": "order_placement",
    "results": [
        {"agent": "CartAgent", "status": "executed"},
        {"agent": "OrderAgent", "status": "executed", "order_id": 1},
        {"agent": "NotificationAgent", "status": "executed", "notification_id": 1}
    ],
    "context": {
        "user_id": 1,
        "order_id": 1,
        "notification_id": 1
    }
}
```

## Agent Communication

Agents communicate through the orchestrator:

```python
# Direct access
product = orchestrator.get_agent("ProductAgent")
products = product.get_all_products()

# Via orchestrator execute method
result = orchestrator.execute("ProductAgent", "get_all_products")
```

## Error Handling

```python
try:
    result = orchestrator.execute_workflow("unknown_workflow")
except ValueError as e:
    print(f"Workflow not found: {e}")

try:
    agent = orchestrator.get_agent("NonExistentAgent")
    if agent is None:
        print("Agent not found")
except Exception as e:
    print(f"Error: {e}")
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| agent_source | agents/agents.md | Path to agent definitions |
| max_workflow_steps | 10 | Maximum steps per workflow |
| timeout | 30 | Workflow timeout in seconds |

## Integration with FastAPI

```python
from agents import orchestrator
from fastapi import APIRouter

router = APIRouter()

@router.get("/agents")
def list_agents():
    return {"agents": orchestrator.list_agents()}

@router.get("/workflows")
def list_workflows():
    return {"workflows": orchestrator.list_workflows()}

@router.post("/workflow/{name}/execute")
def execute_workflow(name: str, context: dict = None):
    return orchestrator.execute_workflow(name, context)
```

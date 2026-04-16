# RecommendationAgent

```yaml
name: RecommendationAgent
version: 1.0.0
description: Provides personalized product recommendations using category-based filtering
storage: none
dependencies:
  - ProductAgent
random_seed: null
recommendation_limits:
  category: 5
  popular: 10
  complementary: 3
  bundle: 3
```

## Overview

RecommendationAgent provides intelligent product recommendations based on various strategies including category similarity, user behavior patterns, and complementary product suggestions. It relies on ProductAgent for product data.

## Capabilities

- Recommend similar products based on a given product
- Recommend products from the same category
- Get popular products (random selection for demo)
- Get complementary products from related categories
- Suggest meal bundle completions
- Filter recommendations by various criteria

## Complementary Categories

Products are suggested from complementary categories for meal planning:

| Category | Complements With |
|----------|-----------------|
| vegetables | fruits |
| fruits | nuts |
| nuts | vegetables |

## Methods

### recommend_by_product(product_id: int)

Gets similar products based on a given product.

```python
def recommend_by_product(self, product_id: int) -> List[Dict]:
    product = self.product_agent.get_product_by_id(product_id)
    if not product:
        return []
    return self.recommend_by_category(product['category'])
```

**Parameters:**
- `product_id` (int) - Product identifier

**Returns:** List of similar products from same category

---

### recommend_by_category(category: str, limit: int = 5)

Gets products from a specific category.

```python
def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
    products = self.product_agent.get_products_by_category(category)
    if len(products) <= limit:
        return products
    return random.sample(products, limit)
```

**Parameters:**
- `category` (str) - Category name
- `limit` (int) - Maximum number of recommendations (default: 5)

**Returns:** List of products from the category

---

### get_popular_products(limit: int = 10)

Gets popular products (random selection for demo purposes).

```python
def get_popular_products(self, limit: int = 10) -> List[Dict]:
    all_products = self.product_agent.get_all_products()
    if len(all_products) <= limit:
        return all_products
    return random.sample(all_products, limit)
```

**Parameters:**
- `limit` (int) - Maximum number of products (default: 10)

**Returns:** List of popular products

---

### get_complementary_products(product_id: int, limit: int = 3)

Gets products from complementary categories.

```python
def get_complementary_products(self, product_id: int, limit: int = 3) -> List[Dict]:
    product = self.product_agent.get_product_by_id(product_id)
    if not product:
        return []
    
    complementary = {
        'vegetables': 'fruits',
        'fruits': 'nuts',
        'nuts': 'vegetables'
    }
    related = complementary.get(product['category'], 'vegetables')
    return self.recommend_by_category(related, limit=limit)
```

**Parameters:**
- `product_id` (int) - Product identifier
- `limit` (int) - Maximum number of products (default: 3)

**Returns:** List of complementary products

---

### get_bundle_suggestions(cart_items: List[Dict], limit: int = 3)

Suggests products to complete a meal bundle based on cart contents.

```python
def get_bundle_suggestions(self, cart_items: List[Dict], limit: int = 3) -> List[Dict]:
    categories = set(item.get('category', '') for item in cart_items)
    suggestions = []
    for category in ['vegetables', 'fruits', 'nuts']:
        if category not in categories:
            products = self.product_agent.get_products_by_category(category)
            if products:
                suggestions.append(random.choice(products))
                if len(suggestions) >= limit:
                    break
    return suggestions
```

**Parameters:**
- `cart_items` (List[Dict]) - Current cart items
- `limit` (int) - Maximum number of suggestions (default: 3)

**Returns:** List of bundle completion suggestions

---

### recommend_related_searches(keyword: str, limit: int = 5)

Suggests related search terms.

```python
def recommend_related_searches(self, keyword: str, limit: int = 5) -> List[str]:
    categories = ['vegetables', 'fruits', 'nuts']
    suggestions = []
    
    keyword_lower = keyword.lower()
    for category in categories:
        if keyword_lower in category or category in keyword_lower:
            suggestions.append(f"organic {category}")
            suggestions.append(f"fresh {category}")
    
    related_terms = ['organic', 'fresh', 'premium', 'seasonal']
    for term in related_terms:
        if term not in keyword_lower:
            suggestions.append(f"{term} {keyword}")
    
    return suggestions[:limit]
```

**Parameters:**
- `keyword` (str) - Current search term
- `limit` (int) - Maximum suggestions (default: 5)

**Returns:** List of related search terms

---

### get_trending_in_category(category: str, limit: int = 5)

Gets trending products in a category.

```python
def get_trending_in_category(self, category: str, limit: int = 5) -> List[Dict]:
    return self.recommend_by_category(category, limit=limit)
```

**Parameters:**
- `category` (str) - Category name
- `limit` (int) - Maximum products (default: 5)

**Returns:** List of trending products

## Usage Example

```python
from agents import get_recommendation_agent, get_product_agent

recommendations = get_recommendation_agent()

# Get similar products
similar = recommendations.recommend_by_product(1)
print(f"Similar to Product 1: {[p['name'] for p in similar]}")

# Get category recommendations
vegetables = recommendations.recommend_by_category('vegetables', limit=5)

# Get popular products
popular = recommendations.get_popular_products(limit=10)

# Get complementary products
# If viewing tomatoes (vegetable), suggest fruits
complementary = recommendations.get_complementary_products(1)
print(f"Complementary: {[p['name'] for p in complementary]}")

# Get bundle suggestions
cart = [
    {'category': 'vegetables', 'name': 'Tomatoes'},
    {'category': 'fruits', 'name': 'Apples'}
]
bundle = recommendations.get_bundle_suggestions(cart)
print(f"Complete your order: {[p['name'] for p in bundle]}")

# Related searches
searches = recommendations.recommend_related_searches('tomato')
print(f"Related searches: {searches}")
```

## Workflow Integration

RecommendationAgent is used in the `product_discovery` workflow:

1. ProductAgent searches/filters products
2. **RecommendationAgent** suggests similar/complementary items

## Recommendation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Similar | Same category products | Product detail page |
| Complementary | Related categories | Cross-selling |
| Popular | Random selection | Homepage |
| Bundle | Missing categories | Cart page |
| Related Search | Search suggestions | Search bar |

## Algorithm Details

### Category-Based Recommendations
```python
def recommend_by_category(category, limit):
    products = get_products_by_category(category)
    return random.sample(products, min(limit, len(products)))
```

### Complementary Product Mapping
```python
complementary_map = {
    'vegetables': 'fruits',  # Veggies go well with fruits
    'fruits': 'nuts',        # Fruits pair with nuts
    'nuts': 'vegetables'     # Nuts complement vegetables
}
```

### Bundle Completion
```python
def get_bundle_suggestions(cart):
    cart_categories = {item['category'] for item in cart}
    all_categories = {'vegetables', 'fruits', 'nuts'}
    missing = all_categories - cart_categories
    # Suggest one product from each missing category
```

## Future Enhancements

- [ ] Add user behavior tracking
- [ ] Implement collaborative filtering
- [ ] Add product ratings to recommendations
- [ ] Include price-based filtering
- [ ] Add seasonal recommendations
- [ ] Implement personalized recommendations based on order history

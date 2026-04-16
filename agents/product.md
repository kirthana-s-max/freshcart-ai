# ProductAgent

```yaml
name: ProductAgent
version: 1.0.0
description: Manages product catalog with data loaded from data/products.csv
storage: csv
data_source: data/products.csv
capabilities:
  - Load and cache products from CSV
  - Search by name, category, or description
  - Filter by category (vegetables, fruits, nuts)
  - Get low stock alerts
  - Get products by ID
```

## Overview

ProductAgent is responsible for all product-related operations in FreshCart AI. It loads product data from a CSV file and provides methods for searching, filtering, and retrieving product information.

## Data Schema

| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique product identifier |
| name | string | Product name |
| category | string | Category (vegetables, fruits, nuts) |
| price | float | Price per unit |
| unit | string | Unit of measurement (kg, bunch, dozen, box) |
| stock | int | Available stock quantity |
| description | string | Product description |
| image_url | string | URL to product image |

## Methods

### get_all_products()

Returns all products from the catalog.

```python
def get_all_products(self) -> List[dict]:
    df = self._load_products()
    return df.to_dict('records')
```

**Returns:** List of all products

---

### get_products_by_category(category: str)

Filters products by category.

```python
def get_products_by_category(self, category: str) -> List[dict]:
    df = self._load_products()
    filtered = df[df['category'].str.lower() == category.lower()]
    return filtered.to_dict('records')
```

**Parameters:**
- `category` - Category name (vegetables, fruits, nuts)

**Returns:** List of products in the category

---

### search_products(keyword: str)

Searches products by name, category, or description.

```python
def search_products(self, keyword: str) -> List[dict]:
    df = self._load_products()
    keyword_lower = keyword.lower()
    filtered = df[
        df['name'].str.lower().str.contains(keyword_lower, na=False) |
        df['category'].str.lower().str.contains(keyword_lower, na=False) |
        df['description'].str.lower().str.contains(keyword_lower, na=False)
    ]
    return filtered.to_dict('records')
```

**Parameters:**
- `keyword` - Search term

**Returns:** List of matching products

---

### get_product_by_id(product_id: int)

Gets a single product by its ID.

```python
def get_product_by_id(self, product_id: int) -> Optional[dict]:
    df = self._load_products()
    product = df[df['id'] == product_id]
    if product.empty:
        return None
    return product.iloc[0].to_dict()
```

**Parameters:**
- `product_id` - Product ID

**Returns:** Product dict or None if not found

---

### get_categories()

Gets all available product categories.

```python
def get_categories(self) -> List[str]:
    df = self._load_products()
    return df['category'].unique().tolist()
```

**Returns:** List of category names

---

### get_low_stock_products(threshold: int = 10)

Gets products with stock below threshold.

```python
def get_low_stock_products(self, threshold: int = 10) -> List[dict]:
    df = self._load_products()
    low_stock = df[df['stock'] < threshold]
    return low_stock.to_dict('records')
```

**Parameters:**
- `threshold` - Stock threshold (default: 10)

**Returns:** List of low-stock products

---

## Dependencies

- **Data Source:** `data/products.csv`

## Usage Example

```python
from agents import get_product_agent

product_agent = get_product_agent()

# Get all products
all_products = product_agent.get_all_products()

# Filter by category
vegetables = product_agent.get_products_by_category("vegetables")

# Search
results = product_agent.search_products("organic")

# Get single product
product = product_agent.get_product_by_id(1)

# Get categories
categories = product_agent.get_categories()
```

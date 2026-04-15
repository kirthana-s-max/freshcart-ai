# FreshCart AI - E-Commerce Platform

A Swiggy-styled subscription-based delivery app for fresh vegetables, fruits, and nuts.

## Features

- **Product Catalog**: Browse vegetables, fruits, and nuts with images
- **Shopping Cart**: Add items, adjust quantities, view totals
- **Subscription Plans**: Daily, weekly, or monthly delivery subscriptions
- **User Authentication**: Login and registration system
- **Order Tracking**: Real-time order status updates
- **Responsive Design**: Mobile-friendly UI

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 3. Open Frontend
Open `frontend/index.html` in your browser

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product by ID
- `GET /api/products/category/{category}` - Filter by category
- `GET /api/search?q=keyword` - Search products
- `GET /api/categories` - List categories

### Subscriptions
- `POST /api/subscriptions` - Create subscription
- `GET /api/subscriptions` - Get user subscriptions
- `DELETE /api/subscriptions/{id}` - Cancel subscription
- `GET /api/subscription-plans` - Get available plans

### Orders
- `POST /api/orders` - Place order
- `GET /api/orders` - Get order history
- `GET /api/orders/{id}` - Get order details
- `GET /api/orders/track/{id}` - Track order

### Cart
- `POST /api/cart/add` - Add item to cart
- `GET /api/cart` - Get cart contents

## Demo Credentials
- Email: demo@freshcart.ai
- Password: demo123

## Project Structure
```
freshcart-ai/
├── api/
│   ├── main.py              # FastAPI app
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   └── routes/
│       ├── user_routes.py    # User management
│       └── product_routes.py # Products, orders, subscriptions
├── data/
│   └── products.csv          # Product data
├── frontend/
│   ├── index.html            # Main HTML
│   ├── css/
│   │   └── styles.css        # Styling
│   └── js/
│       └── app.js            # Frontend logic
├── static/                   # Static assets
├── main.py                   # Entry point
└── requirements.txt         # Dependencies
```

## Tech Stack

**Backend:**
- FastAPI
- Pydantic
- Pandas (for data)

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript
- Font Awesome Icons
- Google Fonts (Poppins)

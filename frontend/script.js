/**
 * FreshCart AI - Complete Frontend JavaScript
 * Full e-commerce flow implementation
 */

const API_BASE = 'http://localhost:8000/api';

let products = [];
let cart = [];
let currentCategory = 'all';
let authToken = localStorage.getItem('freshcart_token');
let currentUser = null;
let appliedPromo = null;
let userOrders = [];
let userSubscriptions = [];
let userNotifications = [];
let notificationPollInterval = null;

const productMeta = {
    1: { rating: 4.5, reviews: 234, delivery: '25-30 min', tag: 'bestseller', discount: 10 },
    2: { rating: 4.3, reviews: 156, delivery: '30-35 min', tag: null, discount: 5 },
    3: { rating: 4.7, reviews: 312, delivery: '25-30 min', tag: 'bestseller', discount: 15 },
    4: { rating: 4.2, reviews: 98, delivery: '30-35 min', tag: null, discount: null },
    5: { rating: 4.4, reviews: 187, delivery: '25-30 min', tag: null, discount: 8 },
    6: { rating: 4.6, reviews: 203, delivery: '30-35 min', tag: null, discount: 12 },
    7: { rating: 4.8, reviews: 456, delivery: '25-30 min', tag: 'bestseller', discount: 20 },
    8: { rating: 4.3, reviews: 289, delivery: '30-35 min', tag: null, discount: 10 },
    9: { rating: 4.5, reviews: 334, delivery: '25-30 min', tag: null, discount: 15 },
    10: { rating: 4.7, reviews: 412, delivery: '30-35 min', tag: 'bestseller', discount: 18 },
    11: { rating: 4.4, reviews: 178, delivery: '25-30 min', tag: 'limited', discount: 25 },
    12: { rating: 4.6, reviews: 267, delivery: '30-35 min', tag: null, discount: 12 },
    13: { rating: 4.5, reviews: 145, delivery: '25-30 min', tag: null, discount: 8 },
    14: { rating: 4.3, reviews: 123, delivery: '30-35 min', tag: null, discount: 10 },
    15: { rating: 4.8, reviews: 198, delivery: '25-30 min', tag: 'bestseller', discount: 15 },
    16: { rating: 4.2, reviews: 87, delivery: '30-35 min', tag: null, discount: null }
};

const productImages = {
    1: 'https://images.unsplash.com/photo-1546470427-e26264be0b0d?w=600&h=400&fit=crop&q=80',
    2: 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600&h=400&fit=crop&q=80',
    3: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600&h=400&fit=crop&q=80',
    4: 'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=600&h=400&fit=crop&q=80',
    5: 'https://images.unsplash.com/photo-1449300079323-02e1d9d3a6dc?w=600&h=400&fit=crop&q=80',
    6: 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=600&h=400&fit=crop&q=80',
    7: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&h=400&fit=crop&q=80',
    8: 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600&h=400&fit=crop&q=80',
    9: 'https://images.unsplash.com/photo-1547514701-42782101795e?w=600&h=400&fit=crop&q=80',
    10: 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=600&h=400&fit=crop&q=80',
    11: 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=600&h=400&fit=crop&q=80',
    12: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=600&h=400&fit=crop&q=80',
    13: 'https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=600&h=400&fit=crop&q=80',
    14: 'https://images.unsplash.com/photo-1599593752329-26b651e2efcc?w=600&h=400&fit=crop&q=80',
    15: 'https://images.unsplash.com/photo-1630431341973-02e1b662ec35?w=600&h=400&fit=crop&q=80',
    16: 'https://images.unsplash.com/photo-1594942895212-a1b77f48ee92?w=600&h=400&fit=crop&q=80'
};

async function api(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json' };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: { ...headers, ...options.headers }
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `API Error: ${response.status}`);
        }
        
        return response.json();
    } catch (error) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            throw new Error('Unable to connect to server. Make sure the API is running on port 8000.');
        }
        throw error;
    }
}

async function init() {
    loadCartFromStorage();
    animateOnLoad();
    showLoadingSkeletons();
    initNotifications();
    
    try {
        products = await api('/products');
        renderProducts();
        updateStats();
    } catch (error) {
        showToast(error.message, 'error');
        document.getElementById('productsGrid').innerHTML = `
            <div style="text-align:center; grid-column: 1/-1; padding: 80px;">
                <div style="font-size: 64px; opacity: 0.2; margin-bottom: 20px;">📦</div>
                <p style="font-size: 18px; color: var(--text-light); margin-bottom: 12px;">Unable to connect to server</p>
                <p style="color: var(--text-light);">Run: <code style="background: var(--bg); padding: 8px 16px; border-radius: 8px; font-family: monospace;">python main.py</code></p>
            </div>
        `;
    }
    
    updateUserArea();
    updateCartUI();
    initQuickFilters();
}

// ==================== NOTIFICATIONS ====================
async function initNotifications() {
    if (authToken) {
        await loadNotifications();
        startNotificationPolling();
    }
}

async function loadNotifications() {
    if (!authToken) return;
    
    try {
        userNotifications = await api('/notifications');
        renderNotifications();
        updateNotificationBadge();
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function updateNotificationBadge() {
    const badge = document.getElementById('notificationCount');
    const unreadCount = userNotifications.filter(n => !n.read).length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

function renderNotifications() {
    const list = document.getElementById('notificationList');
    
    if (userNotifications.length === 0) {
        list.innerHTML = `
            <div class="notification-empty">
                <i class="fas fa-bell-slash"></i>
                <p>No notifications yet</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = userNotifications.map(notification => {
        const iconMap = {
            order: 'fa-bag-shopping',
            delivery: 'fa-truck',
            subscription: 'fa-sync-alt',
            product: 'fa-sparkles'
        };
        
        const timeAgo = getTimeAgo(notification.created_at);
        
        return `
            <div class="notification-item ${notification.read ? '' : 'unread'}" 
                 onclick="handleNotificationClick(${notification.id}, '${notification.type}', ${notification.data?.order_id || notification.data?.subscription_id || notification.data?.product_id || 0})">
                <div class="notification-icon ${notification.type}">
                    <i class="fas ${iconMap[notification.type] || 'fa-bell'}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
                <button class="notification-delete" onclick="event.stopPropagation(); deleteNotification(${notification.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }).join('');
}

function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

function toggleNotifications(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('notificationDropdown');
    dropdown.classList.toggle('open');
    
    if (dropdown.classList.contains('open') && authToken) {
        loadNotifications();
    }
}

function handleNotificationClick(notificationId, type, dataId) {
    markNotificationAsRead(notificationId);
    
    switch (type) {
        case 'order':
        case 'delivery':
            if (dataId) showTracking(dataId);
            break;
        case 'subscription':
            showMySubscriptions();
            break;
        case 'product':
            if (dataId) {
                const product = products.find(p => p.id === dataId);
                if (product) addToCart(dataId);
            }
            break;
    }
}

async function markNotificationAsRead(notificationId) {
    try {
        await api(`/notifications/${notificationId}/read`, { method: 'POST' });
        const notification = userNotifications.find(n => n.id === notificationId);
        if (notification) notification.read = true;
        renderNotifications();
        updateNotificationBadge();
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

async function markAllNotificationsRead() {
    if (!authToken) {
        showToast('Please login to manage notifications', 'info');
        return;
    }
    
    try {
        await api('/notifications/read-all', { method: 'POST' });
        userNotifications.forEach(n => n.read = true);
        renderNotifications();
        updateNotificationBadge();
        showToast('All notifications marked as read', 'success');
    } catch (error) {
        console.error('Error marking all as read:', error);
    }
}

async function deleteNotification(notificationId) {
    try {
        await api(`/notifications/${notificationId}`, { method: 'DELETE' });
        userNotifications = userNotifications.filter(n => n.id !== notificationId);
        renderNotifications();
        updateNotificationBadge();
    } catch (error) {
        console.error('Error deleting notification:', error);
    }
}

function startNotificationPolling() {
    if (notificationPollInterval) clearInterval(notificationPollInterval);
    
    notificationPollInterval = setInterval(() => {
        if (authToken) {
            loadNotifications();
        } else {
            clearInterval(notificationPollInterval);
        }
    }, 30000);
}

function showNotificationToast(notification) {
    const iconMap = {
        order: 'fa-bag-shopping',
        delivery: 'fa-truck',
        subscription: 'fa-sync-alt',
        product: 'fa-sparkles'
    };
    
    const toast = document.getElementById('toast');
    toast.innerHTML = `
        <div class="notification-toast">
            <div class="notification-toast-icon ${notification.type}">
                <i class="fas ${iconMap[notification.type] || 'fa-bell'}"></i>
            </div>
            <div class="notification-toast-content">
                <div class="notification-toast-title">${notification.title}</div>
                <div class="notification-toast-message">${notification.message}</div>
            </div>
        </div>
    `;
    toast.className = `toast show`;
    
    setTimeout(() => toast.classList.remove('show'), 5000);
}

// Demo function to simulate notifications
function simulateNewProductNotification() {
    if (!authToken) return;
    
    const randomProduct = products[Math.floor(Math.random() * products.length)];
    const notification = {
        id: Date.now(),
        type: 'product',
        title: 'New Product Alert! 🌟',
        message: `Check out our new ${randomProduct.name} - now available!`,
        read: false,
        created_at: new Date().toISOString(),
        data: { product_id: randomProduct.id }
    };
    
    userNotifications.unshift(notification);
    renderNotifications();
    updateNotificationBadge();
    showNotificationToast(notification);
}

function showLoadingSkeletons() {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = Array(8).fill().map(() => `
        <div class="skeleton-card">
            <div class="skeleton skeleton-img"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text medium"></div>
            <div class="skeleton skeleton-btn"></div>
        </div>
    `).join('');
}

function hideLoadingSkeletons() {
    // Skeletons are replaced when products load
}

function loadCartFromStorage() {
    const savedCart = localStorage.getItem('freshcart_cart');
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
        } catch (e) {
            cart = [];
        }
    }
}

function saveCartToStorage() {
    localStorage.setItem('freshcart_cart', JSON.stringify(cart));
}

function animateOnLoad() {
    const heroElements = document.querySelectorAll('.hero-content > *');
    heroElements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 + (i * 100));
    });
}

function initQuickFilters() {
    document.querySelectorAll('.quick-filter').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.quick-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.dataset.filter;
            if (filter === 'all') filterProducts('all');
            else if (filter === 'under10') filterByPrice();
            else if (filter === 'bestseller') filterByTag('bestseller');
            else filterProducts(filter);
        });
    });
}

function updateStats() {
    document.getElementById('productCount').textContent = `${products.length} items`;
}

function renderProducts(productList = products) {
    const grid = document.getElementById('productsGrid');
    const filtered = currentCategory === 'all' 
        ? productList 
        : productList.filter(p => p.category === currentCategory);
    
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="text-align:center; grid-column: 1/-1; padding: 80px;">
                <div style="font-size: 64px; opacity: 0.2; margin-bottom: 20px;">🔍</div>
                <p style="font-size: 18px; color: var(--text-light);">No products found</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filtered.map((product, index) => {
        const meta = productMeta[product.id] || { rating: 4.0, reviews: 50, delivery: '30-35 min', tag: null, discount: null };
        const tagClass = meta.tag === 'bestseller' ? 'bestseller' : (meta.tag === 'limited' ? 'limited' : '');
        const imageUrl = productImages[product.id] || product.image_url || `https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&h=400&fit=crop&q=80`;
        
        return `
            <div class="product-card" style="animation-delay: ${index * 0.05}s">
                <div class="product-img">
                    <img src="${imageUrl}" 
                         alt="${product.name}" 
                         loading="lazy"
                         onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&h=400&fit=crop&q=80'">
                    ${meta.tag ? `<span class="product-tag ${tagClass}">${meta.tag.toUpperCase()}</span>` : `<span class="product-tag">${product.category}</span>`}
                    ${meta.discount ? `<span class="discount-badge">${meta.discount}% OFF</span>` : ''}
                    <span class="delivery-badge"><i class="fas fa-clock"></i> ${meta.delivery}</span>
                </div>
                <div class="product-info">
                    <div class="product-header">
                        <h3 class="product-name">${product.name}</h3>
                        <div class="product-rating">
                            <i class="fas fa-star"></i> ${meta.rating}
                            <span>(${meta.reviews})</span>
                        </div>
                    </div>
                    <p class="product-desc">${product.description}</p>
                    <div class="product-bottom">
                        <div class="product-price">
                            ${meta.discount ? `<span class="strike">$${product.price.toFixed(2)}</span>` : ''}
                            $${(product.price * (1 - (meta.discount || 0) / 100)).toFixed(2)}
                            <span>/ ${product.unit}</span>
                        </div>
                        <button class="add-btn" onclick="addToCart(${product.id})">
                            <i class="fas fa-plus"></i> ADD
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function filterProducts(category) {
    currentCategory = category;
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        const isActive = btn.textContent.toLowerCase() === category || (category === 'all' && btn.textContent === 'All');
        btn.classList.toggle('active', isActive);
    });
    
    document.querySelectorAll('.quick-filter').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === category);
    });
    
    document.getElementById('productTitle').textContent = category === 'all' ? 'All Products' : category.charAt(0).toUpperCase() + category.slice(1);
    document.getElementById('productCount').textContent = category === 'all' ? `${products.length} items` : `${products.filter(p => p.category === category).length} items`;
    
    const filtered = category === 'all' ? products : products.filter(p => p.category === category);
    renderProducts(filtered);
    document.getElementById('products').scrollIntoView({ behavior: 'smooth' });
}

function filterByPrice() {
    const filtered = products.filter(p => p.price < 10);
    document.getElementById('productTitle').textContent = 'Under $10';
    document.getElementById('productCount').textContent = `${filtered.length} items`;
    renderProducts(filtered);
}

function filterByTag(tag) {
    const filtered = products.filter(p => (productMeta[p.id] || {}).tag === tag);
    document.getElementById('productTitle').textContent = tag === 'bestseller' ? 'Bestsellers' : 'Limited Offers';
    document.getElementById('productCount').textContent = `${filtered.length} items`;
    renderProducts(filtered);
}

function scrollCategories(direction) {
    const container = document.getElementById('categoriesScroll');
    container.scrollBy({ left: direction * 200, behavior: 'smooth' });
}

document.getElementById('searchInput').addEventListener('input', debounce(async (e) => {
    const query = e.target.value.trim();
    if (query.length > 0) {
        try {
            const results = await api(`/search?q=${encodeURIComponent(query)}`);
            document.getElementById('productTitle').textContent = `Search: "${query}"`;
            document.getElementById('productCount').textContent = `${results.length} results`;
            renderProducts(results);
        } catch (error) { console.error('Search error:', error); }
    } else {
        document.getElementById('productTitle').textContent = 'All Products';
        document.getElementById('productCount').textContent = `${products.length} items`;
        renderProducts();
    }
}, 300));

document.getElementById('heroSearchInput').addEventListener('input', debounce(async (e) => {
    const query = e.target.value.trim();
    if (query.length > 0) {
        try {
            const results = await api(`/search?q=${encodeURIComponent(query)}`);
            renderProducts(results);
            document.getElementById('products').scrollIntoView({ behavior: 'smooth' });
        } catch (error) { console.error('Search error:', error); }
    } else {
        renderProducts();
    }
}, 300));

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const existing = cart.find(item => item.product_id === productId);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1,
            unit: product.unit,
            image_url: product.image_url
        });
    }
    
    saveCartToStorage();
    updateCartUI();
    animateCartBadge();
    showToast(`${product.name} added to cart!`, 'success');
    
    const btn = event.target.closest('.add-btn');
    if (btn) {
        btn.textContent = '✓ Added';
        btn.style.background = 'var(--green)';
        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-plus"></i> ADD';
            btn.style.background = '';
        }, 1000);
    }
}

function animateCartBadge() {
    const badge = document.getElementById('cartBadge');
    badge.style.animation = 'none';
    badge.offsetHeight;
    badge.style.animation = 'bounce 0.5s ease';
    
    const floatingBadge = document.getElementById('floatingBadge');
    if (floatingBadge) floatingBadge.style.animation = 'bounce 0.5s ease';
}

function updateQuantity(productId, delta) {
    const item = cart.find(i => i.product_id === productId);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            saveCartToStorage();
            updateCartUI();
        }
    }
}

function removeFromCart(productId) {
    const item = cart.find(i => i.product_id === productId);
    cart = cart.filter(i => i.product_id !== productId);
    saveCartToStorage();
    updateCartUI();
    if (item) showToast(`${item.name} removed from cart`, 'info');
}

function updateCartUI() {
    const badge = document.getElementById('cartBadge');
    const cartItems = document.getElementById('cartItems');
    const cartFooter = document.getElementById('cartFooter');
    
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    badge.textContent = totalItems;
    badge.style.display = totalItems > 0 ? 'flex' : 'none';
    
    const floatingBadge = document.getElementById('floatingBadge');
    if (floatingBadge) {
        floatingBadge.textContent = totalItems;
        floatingBadge.style.display = totalItems > 0 ? 'flex' : 'none';
    }
    
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="empty-cart">
                <span class="empty-icon">🛒</span>
                <p>Your cart is empty</p>
                <span class="empty-sub">Add items to get started</span>
            </div>
        `;
        cartFooter.style.display = 'none';
    } else {
        cartItems.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-img">
                    <img src="${item.image_url || 'https://via.placeholder.com/80'}" alt="${item.name}">
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">$${item.price.toFixed(2)} × ${item.quantity} = $${(item.price * item.quantity).toFixed(2)}</div>
                    <div class="cart-item-actions">
                        <button class="qty-btn" onclick="updateQuantity(${item.product_id}, -1)">−</button>
                        <span class="qty-val">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity(${item.product_id}, 1)">+</button>
                        <button class="remove-btn" onclick="removeFromCart(${item.product_id})">Remove</button>
                    </div>
                </div>
            </div>
        `).join('');
        
        cartFooter.style.display = 'block';
        
        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        let deliveryFee = 2.99;
        let discount = 0;
        
        if (authToken || subtotal >= 50) deliveryFee = 0;
        if (appliedPromo) {
            discount = appliedPromo.type === 'percent' ? subtotal * (appliedPromo.value / 100) : appliedPromo.value;
        }
        
        const total = subtotal + deliveryFee - discount;
        
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('deliveryFee').textContent = deliveryFee === 0 ? 'FREE' : `$${deliveryFee.toFixed(2)}`;
        document.getElementById('deliveryFee').className = deliveryFee === 0 ? 'discount' : '';
        document.getElementById('discountAmount').textContent = `-$${discount.toFixed(2)}`;
        document.getElementById('total').textContent = `$${total.toFixed(2)}`;
    }
}

function toggleCart() {
    document.getElementById('cartOverlay').classList.toggle('open');
    document.getElementById('cartSidebar').classList.toggle('open');
    document.body.style.overflow = document.getElementById('cartSidebar').classList.contains('open') ? 'hidden' : '';
}

function applyPromo() {
    const input = document.getElementById('promoInput');
    const code = input.value.trim().toUpperCase();
    
    const promos = {
        'FRESH20': { type: 'percent', value: 20, description: '20% off' },
        'VEGGIE15': { type: 'percent', value: 15, description: '15% off' },
        'FIRST10': { type: 'flat', value: 10, description: '$10 off' },
        'PRO5': { type: 'percent', value: 5, description: '5% off' }
    };
    
    if (promos[code]) {
        appliedPromo = promos[code];
        saveCartToStorage();
        updateCartUI();
        showToast(`Promo applied! ${promos[code].description}`, 'success');
        input.value = '';
    } else {
        showToast('Invalid promo code', 'error');
    }
}

async function placeOrder() {
    if (cart.length === 0) {
        showToast('Your cart is empty!', 'error');
        return;
    }
    
    if (!authToken) {
        showToast('Please login to place an order', 'error');
        showLogin();
        return;
    }
    
    const items = cart.map(item => ({
        product_id: item.product_id,
        name: item.name,
        price: item.price,
        quantity: item.quantity
    }));
    
    try {
        const order = await api('/orders', {
            method: 'POST',
            body: JSON.stringify({
                items,
                address: currentUser?.address || '123 Delivery Street, Mumbai, India',
                payment_method: 'cod'
            })
        });
        
        cart = [];
        appliedPromo = null;
        saveCartToStorage();
        updateCartUI();
        toggleCart();
        
        showToast(`Order #${order.id} placed successfully!`, 'success');
        showTracking(order.id);
        
        userOrders.unshift(order);
    } catch (error) {
        showToast(error.message || 'Failed to place order', 'error');
    }
}

async function showTracking(orderId) {
    try {
        const tracking = await api(`/orders/track/${orderId}`);
        
        document.getElementById('trackOrderId').textContent = orderId;
        document.getElementById('etaTime').textContent = tracking.estimated_delivery ? new Date(tracking.estimated_delivery).toLocaleString() : 'Calculating...';
        
        document.getElementById('timeline').innerHTML = tracking.timeline.map((step, index) => {
            const isDone = step.completed;
            const isCurrent = isDone && !tracking.timeline[index + 1]?.completed;
            return `
                <div class="timeline-item ${isDone ? 'done' : ''} ${isCurrent ? 'current' : ''}">
                    <div class="timeline-dot">${isDone ? '✓' : index + 1}</div>
                    <div class="timeline-text">
                        <h4>${step.status}</h4>
                        ${step.time ? `<p>${new Date(step.time).toLocaleString()}</p>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        openModal('trackModal');
    } catch (error) {
        showToast('Unable to load tracking info', 'error');
    }
}

function showSubscriptions() {
    openModal('subModal');
}

function showOffers() {
    openModal('offersModal');
}

async function subscribePlan(frequency) {
    if (!authToken) {
        showToast('Please login first to subscribe', 'error');
        closeModal('subModal');
        setTimeout(showLogin, 500);
        return;
    }
    
    const planProducts = { daily: products[0], weekly: products[1], monthly: products[2] };
    const product = planProducts[frequency] || products[0];
    
    try {
        const subscription = await api('/subscriptions', {
            method: 'POST',
            body: JSON.stringify({
                product_id: product.id,
                frequency,
                quantity: 1
            })
        });
        
        closeModal('subModal');
        showToast(`Subscribed to ${frequency} plan successfully!`, 'success');
        userSubscriptions.unshift(subscription);
    } catch (error) {
        showToast(error.message || 'Subscription failed', 'error');
    }
}

function showRegister() {
    closeModal('loginModal');
    openModal('registerModal');
}

async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const phone = document.getElementById('registerPhone').value.trim();
    const address = document.getElementById('registerAddress').value.trim();
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    const btn = event.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-small"></span> Creating account...';
    
    try {
        const response = await api('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ name, email, phone, address, password })
        });
        
        authToken = response.token;
        currentUser = response.user;
        localStorage.setItem('freshcart_token', authToken);
        
        closeModal('registerModal');
        updateUserArea();
        showToast(`Welcome to FreshCart, ${name}!`, 'success');
        
        document.getElementById('registerForm').reset();
    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
    }
}

function showLogin() {
    openModal('loginModal');
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    const btn = event.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-small"></span> Logging in...';
    
    try {
        const result = await api('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        authToken = result.token;
        currentUser = result.user;
        localStorage.setItem('freshcart_token', authToken);
        
        updateUserArea();
        closeModal('loginModal');
        showToast(`Welcome back, ${currentUser.name}!`, 'success');
        
        loadUserData();
        initNotifications();
    } catch (error) {
        showToast(error.message || 'Login failed. Check your credentials.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    userOrders = [];
    userSubscriptions = [];
    userNotifications = [];
    appliedPromo = null;
    localStorage.removeItem('freshcart_token');
    
    if (notificationPollInterval) {
        clearInterval(notificationPollInterval);
        notificationPollInterval = null;
    }
    
    renderNotifications();
    updateNotificationBadge();
    updateUserArea();
    showToast('Logged out successfully');
}

async function loadUserData() {
    if (!authToken) return;
    
    try {
        const [orders, subscriptions] = await Promise.all([
            api('/orders').catch(() => []),
            api('/subscriptions').catch(() => [])
        ]);
        
        userOrders = orders || [];
        userSubscriptions = subscriptions || [];
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

function updateUserArea() {
    const userArea = document.getElementById('userArea');
    
    if (authToken) {
        if (!currentUser) {
            api('/auth/me')
                .then(user => {
                    currentUser = user;
                    loadUserData();
                    renderUserMenu();
                })
                .catch(() => {
                    authToken = null;
                    localStorage.removeItem('freshcart_token');
                    renderLoginLink();
                });
        } else {
            renderUserMenu();
        }
    } else {
        renderLoginLink();
    }
}

function renderUserMenu() {
    const userArea = document.getElementById('userArea');
    userArea.innerHTML = `
        <div class="user-menu" onclick="openAccount()" style="display:flex; align-items:center; gap:12px; cursor:pointer;">
            <div style="width:36px; height:36px; background:var(--primary); border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:600; font-size:14px;">
                ${currentUser?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span style="font-weight:500; font-size:14px;">${currentUser?.name || 'Account'}</span>
        </div>
    `;
}

function renderLoginLink() {
    const userArea = document.getElementById('userArea');
    userArea.innerHTML = `
        <a href="#" class="nav-link" onclick="showLogin(); return false;">
            <i class="fas fa-user"></i> <span>Login</span>
        </a>
    `;
}

function openAccount() {
    if (!authToken) {
        showLogin();
        return;
    }
    
    document.getElementById('profileAvatar').textContent = currentUser?.name?.charAt(0).toUpperCase() || 'U';
    document.getElementById('profileName').textContent = currentUser?.name || 'User';
    document.getElementById('profileEmail').textContent = currentUser?.email || '';
    
    openModal('accountModal');
}

async function showOrders() {
    openModal('ordersModal');
    
    const content = document.getElementById('ordersContent');
    content.innerHTML = `<div class="orders-loading"><div class="spinner"></div><p>Loading orders...</p></div>`;
    
    if (!authToken) {
        content.innerHTML = `
            <div class="orders-empty">
                <div class="orders-empty-icon">🔒</div>
                <h4>Login Required</h4>
                <p>Please login to view your orders</p>
                <button class="btn btn-primary" onclick="closeModal('ordersModal'); showLogin();" style="margin-top:16px;">Login</button>
            </div>
        `;
        return;
    }
    
    try {
        userOrders = await api('/orders');
        renderOrders('active');
    } catch (error) {
        content.innerHTML = `<div class="orders-empty"><p>Unable to load orders</p></div>`;
    }
}

function switchOrderTab(tab) {
    document.querySelectorAll('.order-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    renderOrders(tab);
}

function renderOrders(tab) {
    const content = document.getElementById('ordersContent');
    
    const activeOrders = userOrders.filter(o => !['delivered', 'cancelled'].includes(o.status));
    const pastOrders = userOrders.filter(o => ['delivered', 'cancelled'].includes(o.status));
    const orders = tab === 'active' ? activeOrders : pastOrders;
    
    if (orders.length === 0) {
        content.innerHTML = `
            <div class="orders-empty">
                <div class="orders-empty-icon">📦</div>
                <h4>No ${tab === 'active' ? 'Active' : 'Past'} Orders</h4>
                <p>${tab === 'active' ? 'You have no orders in progress' : 'Your past orders will appear here'}</p>
                ${tab === 'active' ? `<button class="btn btn-primary" onclick="closeModal('ordersModal'); document.getElementById('products').scrollIntoView();" style="margin-top:16px;">Start Shopping</button>` : ''}
            </div>
        `;
        return;
    }
    
    content.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-card-header">
                <div>
                    <span class="order-id">Order #${order.id}</span>
                    <span class="order-date">${new Date(order.created_at).toLocaleDateString()}</span>
                </div>
                <span class="order-status ${order.status}">${order.status.replace('_', ' ')}</span>
            </div>
            <div class="order-card-body">
                <div class="order-items-list">
                    ${order.items.slice(0, 3).map(item => `
                        <div class="order-item">
                            <span class="order-item-name">${item.name}</span>
                            <span class="order-item-qty">× ${item.quantity}</span>
                        </div>
                    `).join('')}
                    ${order.items.length > 3 ? `<div class="order-item"><span class="order-item-qty">+${order.items.length - 3} more items</span></div>` : ''}
                </div>
            </div>
            <div class="order-card-footer">
                <span class="order-total">$${order.total.toFixed(2)} <span>(${order.payment_method.toUpperCase()})</span></span>
                <button class="track-order-btn" onclick="event.stopPropagation(); showTracking(${order.id});">Track Order</button>
            </div>
        </div>
    `).join('');
}

async function showMySubscriptions() {
    openModal('mySubsModal');
    
    const content = document.getElementById('subscriptionsContent');
    content.innerHTML = `<div class="subscriptions-loading"><div class="spinner"></div><p>Loading subscriptions...</p></div>`;
    
    if (!authToken) {
        content.innerHTML = `
            <div class="subscriptions-empty">
                <div class="subscriptions-empty-icon">🔒</div>
                <h4>Login Required</h4>
                <p>Please login to view your subscriptions</p>
                <button class="btn btn-primary" onclick="closeModal('mySubsModal'); showLogin();" style="margin-top:16px;">Login</button>
            </div>
        `;
        return;
    }
    
    try {
        userSubscriptions = await api('/subscriptions');
        renderSubscriptions();
    } catch (error) {
        content.innerHTML = `<div class="subscriptions-empty"><p>Unable to load subscriptions</p></div>`;
    }
}

function renderSubscriptions() {
    const content = document.getElementById('subscriptionsContent');
    
    if (userSubscriptions.length === 0) {
        content.innerHTML = `
            <div class="subscriptions-empty">
                <div class="subscriptions-empty-icon">🔄</div>
                <h4>No Active Subscriptions</h4>
                <p>Subscribe to a plan and never run out of essentials!</p>
                <button class="btn btn-primary" onclick="closeModal('mySubsModal'); showSubscriptions();" style="margin-top:16px;">View Plans</button>
            </div>
        `;
        return;
    }
    
    const planIcons = { daily: 'fa-leaf', weekly: 'fa-crown', monthly: 'fa-gem' };
    
    content.innerHTML = userSubscriptions.map(sub => `
        <div class="subscription-card ${sub.active ? 'active' : ''}">
            <div class="subscription-card-header">
                <div class="subscription-plan">
                    <div class="subscription-plan-icon">
                        <i class="fas ${planIcons[sub.frequency] || 'fa-crown'}"></i>
                    </div>
                    <div>
                        <div class="subscription-plan-name">${sub.product_name}</div>
                        <div class="subscription-plan-frequency">${sub.frequency.charAt(0).toUpperCase() + sub.frequency.slice(1)} Delivery</div>
                    </div>
                </div>
                <span class="subscription-status ${sub.active ? 'active' : 'cancelled'}">${sub.active ? 'Active' : 'Cancelled'}</span>
            </div>
            <div class="subscription-card-body">
                <div class="subscription-detail">
                    <span class="subscription-detail-label">Quantity</span>
                    <span class="subscription-detail-value">${sub.quantity}</span>
                </div>
                <div class="subscription-detail">
                    <span class="subscription-detail-label">Price per unit</span>
                    <span class="subscription-detail-value">$${sub.price.toFixed(2)}</span>
                </div>
                <div class="subscription-detail">
                    <span class="subscription-detail-label">Total</span>
                    <span class="subscription-detail-value">$${sub.total.toFixed(2)}/delivery</span>
                </div>
            </div>
            <div class="subscription-card-footer">
                <span class="subscription-next">
                    Next delivery: <strong>${sub.active ? new Date(sub.next_delivery).toLocaleDateString() : 'N/A'}</strong>
                </span>
                ${sub.active ? `<button class="cancel-sub-btn" onclick="cancelSubscription(${sub.id})">Cancel</button>` : ''}
            </div>
        </div>
    `).join('');
}

async function cancelSubscription(subId) {
    if (!confirm('Are you sure you want to cancel this subscription?')) return;
    
    try {
        await api(`/subscriptions/${subId}`, { method: 'DELETE' });
        showToast('Subscription cancelled', 'success');
        userSubscriptions = userSubscriptions.map(s => s.id === subId ? {...s, active: false} : s);
        renderSubscriptions();
    } catch (error) {
        showToast('Failed to cancel subscription', 'error');
    }
}

function showAddresses() {
    showToast('Address management coming soon!', 'info');
}

function showEditProfile() {
    showToast('Profile editing coming soon!', 'info');
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('open');
    document.body.style.overflow = '';
}

function showToast(message, type = '') {
    const toast = document.getElementById('toast');
    const icon = type === 'success' ? '<i class="fas fa-check-circle"></i>' :
                 type === 'error' ? '<i class="fas fa-exclamation-circle"></i>' :
                 type === 'info' ? '<i class="fas fa-info-circle"></i>' : '';
    
    toast.innerHTML = `${icon} ${message}`;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

document.addEventListener('DOMContentLoaded', init);

document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('open');
            document.body.style.overflow = '';
        }
    });
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(modal => modal.classList.remove('open'));
        document.body.style.overflow = '';
    }
    if (e.ctrlKey && e.shiftKey && e.key === 'N') {
        e.preventDefault();
        if (authToken) {
            simulateNewProductNotification();
        } else {
            showToast('Please login first to test notifications', 'info');
        }
    }
});

window.simulateNotification = simulateNewProductNotification;

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
// Existing code above...

fetch("http://127.0.0.1:8000/recommend")
  .then(response => response.json())
  .then(data => {
      const recommendationBox = document.getElementById("recommendations");

      recommendationBox.innerHTML = "";

      data.forEach(item => {
          const li = document.createElement("li");
          li.textContent = item;
          recommendationBox.appendChild(li);
      });
  }); 
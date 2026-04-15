const API_BASE = 'http://localhost:8000/api';

let products = [];
let cart = [];
let currentCategory = 'all';
let currentUser = null;
let authToken = localStorage.getItem('authToken');

const categoryIcons = {
    vegetables: '🥬',
    fruits: '🍎',
    nuts: '🥜'
};

async function apiCall(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: { ...headers, ...options.headers }
    });
    
    if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
    }
    
    return res.json();
}

async function loadProducts() {
    try {
        products = await apiCall('/products');
        renderProducts();
        updateStats();
    } catch (err) {
        showToast('Unable to connect to server', 'error');
    }
}

function updateStats() {
    document.getElementById('productCount').textContent = products.length;
    document.getElementById('categoryCount').textContent = [...new Set(products.map(p => p.category))].length;
    document.getElementById('deliveryCount').textContent = '500+';
}

function renderProducts() {
    const grid = document.getElementById('productsGrid');
    const filtered = currentCategory === 'all' 
        ? products 
        : products.filter(p => p.category === currentCategory);
    
    if (filtered.length === 0) {
        grid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; padding: 40px; color: var(--text-muted);">No products found</p>';
        return;
    }
    
    grid.innerHTML = filtered.map(p => `
        <div class="product-card">
            <div class="product-image">
                <img src="${p.image_url || `https://via.placeholder.com/300x200?text=${encodeURIComponent(p.name)}`}" 
                     alt="${p.name}"
                     onerror="this.src='https://via.placeholder.com/300x200?text=${encodeURIComponent(p.name)}'">
                <span class="product-tag">${p.category}</span>
            </div>
            <div class="product-info">
                <h3 class="product-name">${p.name}</h3>
                <p class="product-desc">${p.description}</p>
                <div class="product-footer">
                    <div class="product-price">
                        $${p.price} <span>/ ${p.unit}</span>
                    </div>
                    <button class="add-cart-btn" onclick="addToCart(${p.id})">
                        Add
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterProducts(category) {
    currentCategory = category;
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
    renderProducts();
}

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
    
    updateCartUI();
    showToast(`${product.name} added to cart!`, 'success');
}

function updateQuantity(productId, delta) {
    const item = cart.find(i => i.product_id === productId);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            updateCartUI();
        }
    }
}

function removeFromCart(productId) {
    cart = cart.filter(i => i.product_id !== productId);
    updateCartUI();
}

function updateCartUI() {
    const cartItems = document.getElementById('cartItems');
    const cartFooter = document.getElementById('cartFooter');
    const badge = document.getElementById('cartBadge');
    
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    badge.textContent = totalItems;
    badge.style.display = totalItems > 0 ? 'flex' : 'none';
    
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="cart-empty">
                <div class="cart-empty-icon">🛒</div>
                <p>Your cart is empty</p>
            </div>
        `;
        cartFooter.style.display = 'none';
    } else {
        cartItems.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-image">
                    <img src="${item.image_url || 'https://via.placeholder.com/80'}" alt="${item.name}">
                </div>
                <div class="cart-item-details">
                    <h4 class="cart-item-name">${item.name}</h4>
                    <p class="cart-item-price">$${item.price} x ${item.quantity} = $${(item.price * item.quantity).toFixed(2)}</p>
                    <div class="cart-item-actions">
                        <button class="qty-btn" onclick="updateQuantity(${item.product_id}, -1)">−</button>
                        <span class="qty-value">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity(${item.product_id}, 1)">+</button>
                        <button class="remove-btn" onclick="removeFromCart(${item.product_id})">Remove</button>
                    </div>
                </div>
            </div>
        `).join('');
        cartFooter.style.display = 'block';
        
        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const deliveryFee = 2.99;
        const total = subtotal + deliveryFee;
        
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('deliveryFee').textContent = `$${deliveryFee.toFixed(2)}`;
        document.getElementById('total').textContent = `$${total.toFixed(2)}`;
    }
}

function toggleCart() {
    document.getElementById('cartOverlay').classList.toggle('open');
    document.getElementById('cartSidebar').classList.toggle('open');
}

async function placeOrder() {
    if (cart.length === 0) {
        showToast('Cart is empty!', 'error');
        return;
    }
    
    const items = cart.map(item => ({
        product_id: item.product_id,
        name: item.name,
        price: item.price,
        quantity: item.quantity,
        subtotal: item.price * item.quantity
    }));
    
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    try {
        const order = await apiCall('/orders', {
            method: 'POST',
            body: JSON.stringify({
                items,
                address: '123 Delivery Street, Mumbai, India',
                payment_method: 'cod'
            })
        });
        
        cart = [];
        updateCartUI();
        toggleCart();
        showToast(`Order #${order.id} placed successfully!`, 'success');
        
        document.getElementById('orderId').value = order.id;
        document.getElementById('trackingModal').classList.add('open');
        updateTracking(order.id);
        
    } catch (err) {
        showToast('Failed to place order', 'error');
    }
}

async function updateTracking(orderId) {
    try {
        const tracking = await apiCall(`/orders/track/${orderId}`);
        
        document.getElementById('trackingTimeline').innerHTML = tracking.timeline.map((step, i) => `
            <div class="timeline-item ${step.completed ? 'completed' : ''} ${i === tracking.timeline.findIndex(s => s.completed) && !step.completed ? 'current' : ''}">
                <div class="timeline-dot">${step.completed ? '✓' : i + 1}</div>
                <div class="timeline-content">
                    <h4>${step.status}</h4>
                    ${step.time ? `<p>${new Date(step.time).toLocaleString()}</p>` : ''}
                </div>
            </div>
        `).join('');
        
        document.getElementById('estimatedDelivery').textContent = 
            tracking.estimated_delivery ? new Date(tracking.estimated_delivery).toLocaleString() : 'Calculating...';
        
    } catch (err) {
        console.error('Tracking error:', err);
    }
}

function showSubscriptionModal() {
    document.getElementById('subscriptionModal').classList.add('open');
    loadSubscriptionPlans();
}

async function loadSubscriptionPlans() {
    try {
        const plans = await apiCall('/subscription-plans');
        document.getElementById('plansGrid').innerHTML = plans.map((plan, i) => `
            <div class="plan-card ${i === 1 ? 'featured' : ''}">
                ${i === 1 ? '<span class="plan-badge">POPULAR</span>' : ''}
                <div class="plan-icon">${plan.icon}</div>
                <h3 class="plan-name">${plan.name}</h3>
                <p class="plan-desc">${plan.description}</p>
                <div class="plan-price">${i === 0 ? '$9' : i === 1 ? '$19' : '$29'}<span>/month</span></div>
                <ul class="plan-features">
                    ${plan.benefits.map(b => `<li>${b}</li>`).join('')}
                </ul>
                <button class="plan-btn" onclick="subscribePlan('${plan.id}')">Subscribe Now</button>
            </div>
        `).join('');
    } catch (err) {
        document.getElementById('plansGrid').innerHTML = '<p style="text-align:center; grid-column: 1/-1;">Unable to load plans</p>';
    }
}

async function subscribePlan(frequency) {
    showToast(`Starting ${frequency} subscription...`, 'success');
    closeModal('subscriptionModal');
}

function showAuthModal(type) {
    document.getElementById('authModalTitle').textContent = type === 'login' ? 'Login' : 'Sign Up';
    document.getElementById('authForm').onsubmit = (e) => {
        e.preventDefault();
        handleAuth(type);
    };
    document.getElementById('authModal').classList.add('open');
}

async function handleAuth(type) {
    const form = document.getElementById('authForm');
    const formData = new FormData(form);
    
    try {
        const endpoint = type === 'login' ? '/auth/login' : '/auth/register';
        const data = type === 'login' 
            ? { email: formData.get('email'), password: formData.get('password') }
            : { 
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                address: formData.get('address'),
                password: formData.get('password')
              };
        
        const result = await apiCall(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        authToken = result.token;
        currentUser = result.user;
        localStorage.setItem('authToken', authToken);
        
        updateUserUI();
        closeModal('authModal');
        showToast(`Welcome, ${currentUser.name}!`, 'success');
        
    } catch (err) {
        showToast(type === 'login' ? 'Login failed' : 'Registration failed', 'error');
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateUserUI();
    showToast('Logged out successfully');
}

function updateUserUI() {
    const userSection = document.getElementById('userSection');
    
    if (currentUser) {
        userSection.innerHTML = `
            <div class="user-menu" onclick="showAuthModal('profile')">
                <div class="user-avatar">${currentUser.name.charAt(0)}</div>
                <span>${currentUser.name}</span>
            </div>
        `;
    } else {
        userSection.innerHTML = `
            <a href="#" class="nav-link" onclick="showAuthModal('login')">Login</a>
            <a href="#" class="nav-link" onclick="showAuthModal('register')">Sign Up</a>
        `;
    }
}

function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}

function showToast(message, type = '') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

document.getElementById('searchInput').addEventListener('input', (e) => {
    const keyword = e.target.value.trim();
    if (keyword.length > 0) {
        const results = products.filter(p => 
            p.name.toLowerCase().includes(keyword.toLowerCase()) ||
            p.category.toLowerCase().includes(keyword.toLowerCase())
        );
        renderFilteredProducts(results, keyword);
    } else {
        renderProducts();
    }
});

function renderFilteredProducts(results, keyword) {
    const grid = document.getElementById('productsGrid');
    document.getElementById('sectionTitle').textContent = `Search: "${keyword}"`;
    
    if (results.length === 0) {
        grid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; padding: 40px; color: var(--text-muted);">No products found</p>';
        return;
    }
    
    grid.innerHTML = results.map(p => `
        <div class="product-card">
            <div class="product-image">
                <img src="${p.image_url || `https://via.placeholder.com/300x200?text=${encodeURIComponent(p.name)}`}" 
                     alt="${p.name}">
                <span class="product-tag">${p.category}</span>
            </div>
            <div class="product-info">
                <h3 class="product-name">${p.name}</h3>
                <p class="product-desc">${p.description}</p>
                <div class="product-footer">
                    <div class="product-price">
                        $${p.price} <span>/ ${p.unit}</span>
                    </div>
                    <button class="add-cart-btn" onclick="addToCart(${p.id})">Add</button>
                </div>
            </div>
        </div>
    `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    updateCartUI();
    updateUserUI();
    
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('open');
            }
        });
    });
});

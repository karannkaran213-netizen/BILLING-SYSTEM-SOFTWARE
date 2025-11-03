// Global variables
let currentOrderId = null;

// Add item to cart
function addToCart(itemId, itemName, itemPrice) {
    fetch('/billing/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            menu_item_id: itemId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            loadCart();
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding item to cart', 'error');
    });
}

// Load cart contents
function loadCart() {
    fetch('/billing/cart/get/')
        .then(response => response.json())
        .then(data => {
            updateCartDisplay(data.cart, data.total);
            updateCartCount(data.cart_count);
            document.getElementById('createOrderBtn').disabled = data.cart.length === 0;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Update cart display
function updateCartDisplay(cart, total) {
    const cartItems = document.getElementById('cartItems');
    
    if (cart.length === 0) {
        cartItems.innerHTML = '<p class="empty-cart">Cart is empty</p>';
        return;
    }
    
    let html = '';
    cart.forEach(item => {
        const subtotal = parseFloat(item.price) * item.quantity;
        html += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">₹${item.price} each</div>
                </div>
                <div class="cart-item-quantity">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                    <input type="number" class="quantity-input" value="${item.quantity}" 
                           min="1" onchange="updateQuantity(${item.id}, parseInt(this.value))">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                </div>
                <div class="cart-item-subtotal">₹${subtotal.toFixed(2)}</div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">Remove</button>
            </div>
        `;
    });
    
    cartItems.innerHTML = html;
    document.getElementById('cartTotal').textContent = parseFloat(total).toFixed(2);
}

// Update quantity
function updateQuantity(itemId, quantity) {
    if (quantity < 1) {
        removeFromCart(itemId);
        return;
    }
    
    fetch('/billing/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            menu_item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCart();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating quantity', 'error');
    });
}

// Remove from cart
function removeFromCart(itemId) {
    fetch('/billing/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            menu_item_id: itemId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCart();
            showNotification('Item removed from cart', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error removing item', 'error');
    });
}

// Clear cart
function clearCart() {
    if (!confirm('Are you sure you want to clear the cart?')) {
        return;
    }
    
    fetch('/billing/cart/clear/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadCart();
            showNotification('Cart cleared', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error clearing cart', 'error');
    });
}

// Create order
function createOrder() {
    fetch('/billing/order/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentOrderId = data.order_id;
            // Redirect to bill page
            window.location.href = `/billing/bill/${data.order_id}/`;
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error creating order', 'error');
    });
}

// View bill
function viewBill() {
    if (currentOrderId) {
        window.location.href = `/billing/bill/${currentOrderId}/`;
    } else {
        showNotification('No order found', 'error');
    }
}

// Show bill modal
function showBillModal() {
    const modal = document.getElementById('billModal');
    if (modal) {
        modal.classList.add('show');
    }
}

// Close bill modal
function closeBillModal() {
    const modal = document.getElementById('billModal');
    if (modal) {
        modal.classList.remove('show');
        currentOrderId = null;
    }
}

// Toggle cart section
function toggleCart() {
    const cartSection = document.getElementById('cartSection');
    if (cartSection) {
        cartSection.style.display = cartSection.style.display === 'none' ? 'block' : 'none';
    }
}

// Update cart count
function updateCartCount(count) {
    const cartCount = document.getElementById('cartCount');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

// Pay now
function payNow(orderId) {
    fetch(`/billing/bill/${orderId}/pay/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error processing payment', 'error');
    });
}

// Print bill
function printBill() {
    const billContent = document.getElementById('billContent');
    if (billContent) {
        const printWindow = window.open('', '', 'height=600,width=800');
        printWindow.document.write('<html><head><title>Print Bill</title>');
        printWindow.document.write('<style>');
        printWindow.document.write(`
            body { font-family: Arial, sans-serif; padding: 20px; }
            .bill-header { text-align: center; margin-bottom: 20px; }
            .bill-table { width: 100%; border-collapse: collapse; }
            .bill-table th, .bill-table td { padding: 10px; border: 1px solid #ddd; }
            .bill-total-row { font-weight: bold; }
            @media print { body { margin: 0; } }
        `);
        printWindow.document.write('</style></head><body>');
        printWindow.document.write(billContent.innerHTML);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.print();
    } else {
        window.print();
    }
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'error'}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Load cart on page load
document.addEventListener('DOMContentLoaded', function() {
    loadCart();
});


document.addEventListener('DOMContentLoaded', function() {
    let cart = [];
    const cartItems = document.getElementById('cart-items');
    const paymentSection = document.getElementById('payment-section');

    // Product category switching
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const category = this.dataset.category;
            document.querySelectorAll('.product-grid').forEach(grid => {
                grid.classList.add('hidden');
            });
            document.getElementById(`${category}-products`).classList.remove('hidden');
        });
    });

    // Add to cart functionality
    document.querySelectorAll('.product-item').forEach(item => {
        item.addEventListener('click', function() {
            const id = this.dataset.id;
            const name = this.dataset.name;
            const price = parseFloat(this.dataset.price);
            
            const existingItem = cart.find(item => item.id === id);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({ id, name, price, quantity: 1 });
            }
            updateCart();
        });
    });

    function updateCart() {
        cartItems.innerHTML = cart.map(item => `
            <div class="flex items-center justify-between bg-white p-4 rounded-lg">
                <div>
                    <h3 class="font-medium">${item.name}</h3>
                    <p class="text-sm text-gray-500">₱${item.price.toFixed(2)} × ${item.quantity}</p>
                </div>
                <div class="flex items-center space-x-2">
                    <button class="qty-btn" data-id="${item.id}" data-change="-1">-</button>
                    <span>${item.quantity}</span>
                    <button class="qty-btn" data-id="${item.id}" data-change="1">+</button>
                    <button class="remove-btn" data-id="${item.id}">×</button>
                </div>
            </div>
        `).join('');

        if (cart.length > 0) {
            updatePaymentSection();
        } else {
            paymentSection.innerHTML = '<p class="text-center text-gray-500">Cart is empty</p>';
        }
    }

    // Payment processing
    function updatePaymentSection() {
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        paymentSection.innerHTML = `
            <div class="border-t pt-4">
                <div class="flex justify-between mb-4">
                    <span class="font-bold">Total:</span>
                    <span class="font-bold">₱${total.toFixed(2)}</span>
                </div>
                <div class="grid grid-cols-3 gap-2">
                    <button class="payment-btn" data-method="cash">Cash</button>
                    <button class="payment-btn" data-method="card">Card</button>
                    <button class="payment-btn" data-method="wallet">E-Wallet</button>
                </div>
            </div>
        `;
    }
});

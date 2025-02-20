console.log("script.js loaded!");

function initSlider() {
    const container = document.querySelector('.product-cards');
    const leftBtn = document.querySelector('.arrow-btn.left');
    const rightBtn = document.querySelector('.arrow-btn.right');
    const cards = document.querySelectorAll('.product-card');
    
    if (cards.length > 0) {
        let currentPosition = 0;
        const cardWidth = cards[0].offsetWidth + 20;
        const visibleCards = 4;
        const moveAmount = cardWidth * 3;
        const maxPosition = -(Math.ceil((cards.length - visibleCards) / 3) * moveAmount);

        // Initially hide the left arrow.
        leftBtn.style.display = 'none';

        function updateArrowVisibility() {
            leftBtn.style.display = currentPosition < 0 ? 'flex' : 'none';
            rightBtn.style.display = currentPosition > maxPosition ? 'flex' : 'none';
        }

        function slideProducts(direction) {
            if (direction === 'right') {
                currentPosition = Math.max(currentPosition - moveAmount, maxPosition);
            } else {
                currentPosition = Math.min(currentPosition + moveAmount, 0);
            }
            container.style.transform = `translateX(${currentPosition}px)`;
            updateArrowVisibility();
        }

        rightBtn.addEventListener('click', () => slideProducts('right'));
        leftBtn.addEventListener('click', () => slideProducts('left'));
        updateArrowVisibility();
    }
}

function initQuantityControls() {
    document.querySelectorAll('.qty-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const isMinus = e.currentTarget.classList.contains('minus');
            const input = e.currentTarget.closest('.quantity-control').querySelector('.quantity-input');
            let value = parseInt(input.value) || 1;
            if (isMinus) {
                value = Math.max(1, value - 1);
            } else {
                value += 1;
            }
            input.value = value;
        });
    });
}

function initAddToCart() {
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const prodButton = e.currentTarget;
            const productId = prodButton.getAttribute('data-id');
            const quantityInput = prodButton.closest('.product-card').querySelector('.quantity-input');
            const quantity = parseInt(quantityInput.value) || 1;

            fetch(`/website/add-to-cart/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                updateCartCounter();
                alert(`${data.product_name} has been added to your cart!`);
            })
            .catch(error => console.error('Error:', error));
        });
    });
}

function initRemoveFromCart() {
    document.querySelectorAll('.remove-from-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const prodButton = e.currentTarget;
            const productId = prodButton.getAttribute('data-id');

            fetch(`/website/remove-from-cart/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/website/cart/';
                } else {
                    return response.json().then(data => {
                        throw new Error(data.error);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
}

function updateCartCounter() {
    fetch('/website/cart-count/')
    .then(response => response.json())
    .then(data => {
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = data.count;
        }
    })
    .catch(error => console.error('Error:', error));
}

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

document.addEventListener('DOMContentLoaded', function() {
    initSlider();
    initQuantityControls();
    initAddToCart();
    initRemoveFromCart();
    updateCartCounter();
});
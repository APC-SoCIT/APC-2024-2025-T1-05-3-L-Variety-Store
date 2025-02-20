document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.product-cards');
    const leftBtn = document.querySelector('.arrow-btn.left');
    const rightBtn = document.querySelector('.arrow-btn.right');
    const cards = document.querySelectorAll('.product-card');
    
    let currentPosition = 0;
    const cardWidth = cards[0].offsetWidth + 20;
    const visibleCards = 4;
    const moveAmount = cardWidth * 3;
    const maxPosition = -(Math.ceil((cards.length - visibleCards) / 3) * moveAmount);

    // Initially hide left arrow
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

    rightBtn.addEventListener('click', () => {
        slideProducts('right');
    });

    leftBtn.addEventListener('click', () => {
        slideProducts('left');
    });

    updateArrowVisibility();

    // Select the navbar element
    const navbar = document.querySelector('.navbar');

    // Change background color on mouse enter
    navbar.addEventListener('mouseenter', () => {
        navbar.style.backgroundColor = '#f8d7da'; // Change to light pink
    });

    // Change background color back on mouse leave
    navbar.addEventListener('mouseleave', () => {
        navbar.style.backgroundColor = 'white'; // Change back to white
    });

    // Change background color of navbar when hovering over links
    const navLinks = document.querySelectorAll('.navbar a');

    navLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            navbar.style.backgroundColor = '#f8d7da'; // Change to light pink on link hover
        });

        link.addEventListener('mouseleave', () => {
            navbar.style.backgroundColor = 'white'; // Change back to white when not hovering
        });
    });
}); 
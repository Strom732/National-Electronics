// Object to store the current slide position for each carousel
let carouselPositions = {};

// Function to move the specific carousel
function moveCarousel(carouselId, direction) {
    const carouselContainer = document.getElementById(carouselId);
    const carousel = carouselContainer.querySelector('.carousel');
    const cards = carouselContainer.querySelectorAll('.card');

    if (cards.length === 0) return;

    const cardWidth = cards[0].offsetWidth + 40; // Including margin
    const totalCards = cards.length;
    const visibleCards = Math.floor(carouselContainer.offsetWidth / cardWidth);

    // Initialize position if not already set
    if (!(carouselId in carouselPositions)) {
        carouselPositions[carouselId] = 0;
    }

    carouselPositions[carouselId] += direction;

    // Prevent out-of-bounds scrolling
    if (carouselPositions[carouselId] < 0) {
        carouselPositions[carouselId] = 0;
    } else if (carouselPositions[carouselId] > totalCards - visibleCards) {
        carouselPositions[carouselId] = totalCards - visibleCards;
    }

    const newTransform = -carouselPositions[carouselId] * cardWidth;
    carousel.style.transform = `translateX(${newTransform}px)`;
}

// Function to enable touch swipe on the carousel
function enableTouchSwipe(carouselId) {
    const carouselContainer = document.getElementById(carouselId);
    const carousel = carouselContainer.querySelector('.carousel');
    let startX = 0;
    let endX = 0;

    carousel.addEventListener('touchstart', function (e) {
        startX = e.touches[0].clientX;
    });

    carousel.addEventListener('touchmove', function (e) {
        endX = e.touches[0].clientX;
    });

    carousel.addEventListener('touchend', function () {
        const threshold = 50; // Minimum swipe distance
        const deltaX = endX - startX;

        if (Math.abs(deltaX) > threshold) {
            if (deltaX > 0) {
                moveCarousel(carouselId, -1); // Swipe right
            } else {
                moveCarousel(carouselId, 1); // Swipe left
            }
        }
    });
}

// Initialize touch swipe for each carousel
document.addEventListener('DOMContentLoaded', function () {
    enableTouchSwipe('featured-carousel');
    enableTouchSwipe('SMD-IC-carousel');
});

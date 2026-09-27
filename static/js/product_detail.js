let slideIndex = 1;
showSlides(slideIndex);

// Next/Previous Controls
function plusSlides(n) {
    showSlides(slideIndex += n);
}

// Thumbnail Click Controls
function currentSlide(n) {
    showSlides(slideIndex = n);
}

function showSlides(n) {
    let slides = document.getElementsByClassName("mySlides");
    let dots = document.getElementsByClassName("demo");

    if (n > slides.length) { slideIndex = 1 }
    if (n < 1) { slideIndex = slides.length }

    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (let i = 0; i < dots.length; i++) {
        dots[i].classList.remove("active");
    }

    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].classList.add("active");
}

// Ensure the primary image is shown first on load
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("mainImage").style.display = "block";
});

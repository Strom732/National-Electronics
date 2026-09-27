document.addEventListener('DOMContentLoaded', function () {
  let slideIndex = 0;
  const slides = document.querySelectorAll('.slide');

  function showSlide() {
    slides.forEach(slide => slide.style.display = 'none');
    slideIndex++;
    if (slideIndex > slides.length) slideIndex = 1;
    slides[slideIndex - 1].style.display = 'block';
    setTimeout(showSlide, 3000); // Change slide every 3 seconds (adjust as needed)
  }

  // Initially show the first slide
  if (slides.length > 0) {
    slides[0].style.display = 'block';
  }

  showSlide();
});
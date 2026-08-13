// M6 Fornyelse - Interaktiv Applikasjonslogikk

let isDragging = false;

// Skillelinje (Slider) Drag Logikk
function initSlider() {
  const sliderContainer = document.getElementById('sliderContainer');
  const sliderHandle = document.getElementById('sliderHandle');
  const beforeWrapper = document.getElementById('beforeWrapper');
  const imgBefore = document.getElementById('imgBefore');

  if (!sliderContainer || !sliderHandle || !beforeWrapper || !imgBefore) return;

  function moveSlider(clientX) {
    const rect = sliderContainer.getBoundingClientRect();
    let x = clientX - rect.left;
    if (x < 0) x = 0;
    if (x > rect.width) x = rect.width;

    const percent = (x / rect.width) * 100;
    beforeWrapper.style.width = `${percent}%`;
    sliderHandle.style.left = `${percent}%`;
    imgBefore.style.width = `${rect.width}px`;
  }

  sliderHandle.addEventListener('mousedown', (e) => {
    isDragging = true;
    e.preventDefault();
  });

  window.addEventListener('mouseup', () => { isDragging = false; });
  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    moveSlider(e.clientX);
  });

  sliderContainer.addEventListener('click', (e) => {
    if (e.target.closest('.slider-handle-button')) return;
    moveSlider(e.clientX);
  });

  sliderHandle.addEventListener('touchstart', () => { isDragging = true; });
  window.addEventListener('touchend', () => { isDragging = false; });
  window.addEventListener('touchmove', (e) => {
    if (!isDragging || !e.touches[0]) return;
    moveSlider(e.touches[0].clientX);
  });

  window.addEventListener('resize', () => {
    const rect = sliderContainer.getBoundingClientRect();
    if (imgBefore) imgBefore.style.width = `${rect.width}px`;
  });

  const rect = sliderContainer.getBoundingClientRect();
  imgBefore.style.width = `${rect.width}px`;
}

// Bytte Visningsmodus (Skillelinje vs Side-ved-side)
function setViewMode(mode) {
  const sliderContainer = document.getElementById('sliderContainer');
  const sideContainer = document.getElementById('sideContainer');
  const btnSlider = document.getElementById('btnSliderView');
  const btnSide = document.getElementById('btnSideView');
  const imgBefore = document.getElementById('imgBefore');

  if (mode === 'slider') {
    if (sliderContainer) sliderContainer.style.display = 'block';
    if (sideContainer) sideContainer.style.display = 'none';
    if (btnSlider) btnSlider.classList.add('active');
    if (btnSide) btnSide.classList.remove('active');
    if (sliderContainer && imgBefore) {
      const rect = sliderContainer.getBoundingClientRect();
      imgBefore.style.width = `${rect.width}px`;
    }
  } else {
    if (sliderContainer) sliderContainer.style.display = 'none';
    if (sideContainer) sideContainer.style.display = 'grid';
    if (btnSide) btnSide.classList.add('active');
    if (btnSlider) btnSlider.classList.remove('active');
  }
}

// Varselmeldinger (Toasts)
function showToast(message) {
  const toast = document.getElementById('toastNotification');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// Ved Sidelasting
document.addEventListener('DOMContentLoaded', () => {
  initSlider();
});

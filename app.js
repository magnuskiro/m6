// M6 Renew - Multi-Page Application Logic

// Room Data Definitions
const roomsData = {
  exterior: {
    title: 'Exterior & Facade Transformation',
    details: 'Replacing degraded 1974 wooden siding with Shou Sugi Ban burned timber, installing triple-glazed Schüco floor-to-ceiling glass sliding walls, standing seam metal roofing, and integrated warm LED architectural cove lighting.',
    status: 'Envelope Complete',
    statusClass: 'status-completed',
    beforeImg: 'assets/images/exterior_before.jpg',
    afterImg: 'assets/images/exterior_after.jpg'
  },
  living: {
    title: 'Open-Concept Living & Lounge Area',
    details: 'Removal of partition walls to expand floor plan to 65 m², insertion of HEB 220 steel load-bearing support, continuous light natural oak flooring, concrete feature fireplace, and recessed acoustic ceiling LED cove.',
    status: 'Finishes Pending',
    statusClass: 'status-progress',
    beforeImg: 'assets/images/living_before.jpg',
    afterImg: 'assets/images/living_after.jpg'
  },
  kitchen: {
    title: 'Modern Chef Kitchen & Waterfall Island',
    details: 'Complete gutting of 1970s yellow laminate cabinets, replaced with dark matte handleless cabinetry, white oak accents, 3.2m marble waterfall island, integrated Gaggenau appliances, and induction downdraft cooktop.',
    status: 'Cabinets Ordered',
    statusClass: 'status-progress',
    beforeImg: 'assets/images/kitchen_before.jpg',
    afterImg: 'assets/images/kitchen_after.jpg'
  },
  bathroom: {
    title: 'Master Spa Bathroom & Sauna',
    details: 'Transforming original dated bath into a minimalist luxury spa with Italian large-format porcelain slabs, micro-cement walls, concealed thermostatic valves, walk-in rain shower, freestanding tub, and integrated cedar sauna.',
    status: 'Plumbing Rough-In',
    statusClass: 'status-progress',
    beforeImg: 'assets/images/living_before.jpg',
    afterImg: 'assets/images/living_after.jpg'
  }
};

let currentRoom = 'exterior';
let isDragging = false;

// Initialize Visualizer Slider Drag Functionality
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

// Switch Selected Room
function switchRoom(roomKey) {
  if (!roomsData[roomKey]) return;
  currentRoom = roomKey;
  const data = roomsData[roomKey];

  const imgBefore = document.getElementById('imgBefore');
  const imgAfter = document.getElementById('imgAfter');
  const sideImgBefore = document.getElementById('sideImgBefore');
  const sideImgAfter = document.getElementById('sideImgAfter');
  const beforeWrapper = document.getElementById('beforeWrapper');
  const sliderHandle = document.getElementById('sliderHandle');
  const sliderContainer = document.getElementById('sliderContainer');

  const roomTitle = document.getElementById('roomTitle');
  const roomDetails = document.getElementById('roomDetails');
  const roomStatusBadge = document.getElementById('roomStatusBadge');

  const buttons = document.querySelectorAll('.room-btn');
  buttons.forEach(btn => btn.classList.remove('active'));
  if (event && event.currentTarget) event.currentTarget.classList.add('active');

  if (imgBefore) imgBefore.src = data.beforeImg;
  if (imgAfter) imgAfter.src = data.afterImg;
  if (sideImgBefore) sideImgBefore.src = data.beforeImg;
  if (sideImgAfter) sideImgAfter.src = data.afterImg;

  if (beforeWrapper) beforeWrapper.style.width = '50%';
  if (sliderHandle) sliderHandle.style.left = '50%';

  if (roomTitle) roomTitle.textContent = data.title;
  if (roomDetails) roomDetails.textContent = data.details;
  if (roomStatusBadge) {
    roomStatusBadge.textContent = data.status;
    roomStatusBadge.className = `status-badge ${data.statusClass}`;
  }

  if (sliderContainer && imgBefore) {
    const rect = sliderContainer.getBoundingClientRect();
    imgBefore.style.width = `${rect.width}px`;
  }
}

// View Mode Toggle (Slider vs Side-by-Side)
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

// Copy NotebookLM Source Text
function copySourceContent(sourceId) {
  const sourceTexts = {
    1: "M6 Rehabilitation - Project Overview\nLocation: Myrteveien 6, Tolvsrød (Gnr 140 / Bnr 371)\nGoal: Transform 1974 vintage building into zero-net ready Scandinavian home with TEK17 thermal specs.",
    2: "M6 Technical Specs:\nWall insulation: 200mm Rockwool exterior + Shou Sugi Ban timber cladding.\nHeat Source: NIBE Air-to-Water inverter heat pump.\nWindows: Schüco triple-pane aluminum (Uw = 0.78 W/m²K).",
    3: "M6 Budget Breakdown:\nTotal Allocated: €220,000 | Spent to date: €98,500\nKey Contractors: Nordic Build AS, Thermic Flow AS, Volta Tech AS.",
    4: "M6 Master Timeline:\nPhase 1: Permits & Demolition (Done)\nPhase 2: Envelope & Roofing (Done)\nPhase 3: Technical & Floor Heating (In Progress)\nPhase 4: Interior & Kitchen (Planned)",
    5: "M6 Recommended 9-Stage Building Sequence (Byggerekkefølge):\nStage 1: Permits & Rigging\nStage 2: Demolition & Utrensing\nStage 3: Foundation, Drainage & Radon\nStage 4: Structural Steel (HEB 220)\nStage 5: Building Envelope Weather-tightness\nStage 6: Technical Rough-In (Electrical, PEX, HRV)\nStage 7: Insulation, Vapor Barrier (INTELLO) & Boarding\nStage 8: Wet Rooms (BVN) & Oak Flooring\nStage 9: Commissioning & Occupancy Permit",
    6: "M6 Tønsberg Municipal Plan & Zoning Dependencies:\nKommune: Tønsberg (Kommune-nr: 3905, Gnr 140 / Bnr 371)\nSite Limits: Max 25% BYA (M6 planned: 21.5% BYA)\nBuilding Height: Max 9.0m ridge height / 6.5m cornice height\nSetback: 4.0m boundary setback (PBL § 29-4)\nStormwater: Open local stormwater infiltration (LOD) required"
  };

  const text = sourceTexts[sourceId] || "";
  navigator.clipboard.writeText(text).then(() => {
    showToast(`Source 0${sourceId} text copied to clipboard!`);
  });
}

// Copy NotebookLM Prompt
function copyPrompt() {
  const promptEl = document.getElementById('promptText');
  if (!promptEl) return;
  navigator.clipboard.writeText(promptEl.innerText).then(() => {
    showToast("NotebookLM prompt copied!");
  });
}

// Modal Controls
function openNotebookModal() {
  const modal = document.getElementById('notebookModal');
  if (modal) modal.classList.add('active');
}

function closeNotebookModal() {
  const modal = document.getElementById('notebookModal');
  if (modal) modal.classList.remove('active');
}

// Toast Notifications
function showToast(message) {
  const toast = document.getElementById('toastNotification');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// On Page Load
document.addEventListener('DOMContentLoaded', () => {
  initSlider();
});

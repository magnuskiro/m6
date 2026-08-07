// M6 Renew - Interactive Application Logic

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
    beforeImg: 'assets/images/living_before.jpg', // fallback high quality illustration
    afterImg: 'assets/images/living_after.jpg'
  }
};

let currentRoom = 'exterior';
let isDragging = false;

// DOM Elements
const sliderContainer = document.getElementById('sliderContainer');
const beforeWrapper = document.getElementById('beforeWrapper');
const sliderHandle = document.getElementById('sliderHandle');
const imgBefore = document.getElementById('imgBefore');
const imgAfter = document.getElementById('imgAfter');

const sideContainer = document.getElementById('sideContainer');
const sideImgBefore = document.getElementById('sideImgBefore');
const sideImgAfter = document.getElementById('sideImgAfter');

const roomTitle = document.getElementById('roomTitle');
const roomDetails = document.getElementById('roomDetails');
const roomStatusBadge = document.getElementById('roomStatusBadge');

// Initialize Visualizer Slider Drag Functionality
function initSlider() {
  if (!sliderContainer || !sliderHandle) return;

  function moveSlider(clientX) {
    const rect = sliderContainer.getBoundingClientRect();
    let x = clientX - rect.left;
    if (x < 0) x = 0;
    if (x > rect.width) x = rect.width;

    const percent = (x / rect.width) * 100;
    beforeWrapper.style.width = `${percent}%`;
    sliderHandle.style.left = `${percent}%`;
    
    // Ensure image inner width matches container width so it clips properly without distortion
    imgBefore.style.width = `${rect.width}px`;
  }

  // Mouse Events
  sliderHandle.addEventListener('mousedown', (e) => {
    isDragging = true;
    e.preventDefault();
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    moveSlider(e.clientX);
  });

  // Click anywhere on container to move handle
  sliderContainer.addEventListener('click', (e) => {
    if (e.target.closest('.slider-handle-button')) return;
    moveSlider(e.clientX);
  });

  // Touch Events for Mobile
  sliderHandle.addEventListener('touchstart', () => {
    isDragging = true;
  });

  window.addEventListener('touchend', () => {
    isDragging = false;
  });

  window.addEventListener('touchmove', (e) => {
    if (!isDragging || !e.touches[0]) return;
    moveSlider(e.touches[0].clientX);
  });

  // Handle window resize
  window.addEventListener('resize', () => {
    const rect = sliderContainer.getBoundingClientRect();
    imgBefore.style.width = `${rect.width}px`;
  });

  // Initial calculation
  const rect = sliderContainer.getBoundingClientRect();
  imgBefore.style.width = `${rect.width}px`;
}

// Switch Selected Room
function switchRoom(roomKey) {
  if (!roomsData[roomKey]) return;
  currentRoom = roomKey;
  const data = roomsData[roomKey];

  // Update button active state
  const buttons = document.querySelectorAll('.room-btn');
  buttons.forEach(btn => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');

  // Update Images
  imgBefore.src = data.beforeImg;
  imgAfter.src = data.afterImg;
  sideImgBefore.src = data.beforeImg;
  sideImgAfter.src = data.afterImg;

  // Reset handle position to center 50%
  beforeWrapper.style.width = '50%';
  sliderHandle.style.left = '50%';

  // Update Info Text
  roomTitle.textContent = data.title;
  roomDetails.textContent = data.details;
  roomStatusBadge.textContent = data.status;
  roomStatusBadge.className = `status-badge ${data.statusClass}`;

  // Recalculate inner image bounds
  const rect = sliderContainer.getBoundingClientRect();
  imgBefore.style.width = `${rect.width}px`;
}

// View Mode Toggle (Slider vs Side-by-Side)
function setViewMode(mode) {
  const btnSlider = document.getElementById('btnSliderView');
  const btnSide = document.getElementById('btnSideView');

  if (mode === 'slider') {
    sliderContainer.style.display = 'block';
    sideContainer.style.display = 'none';
    btnSlider.classList.add('active');
    btnSide.classList.remove('active');
    const rect = sliderContainer.getBoundingClientRect();
    imgBefore.style.width = `${rect.width}px`;
  } else {
    sliderContainer.style.display = 'none';
    sideContainer.style.display = 'grid';
    btnSide.classList.add('active');
    btnSlider.classList.remove('active');
  }
}

// Copy NotebookLM Source Text
function copySourceContent(sourceId) {
  const sourceTexts = {
    1: "M6 Rehabilitation - Project Overview\nLocation: M6 Residence | Target Living Area: 220 m²\nGoal: Transform 1974 vintage building into zero-net ready Scandinavian home with TEK17 thermal specs.",
    2: "M6 Technical Specs:\nWall insulation: 200mm Rockwool exterior + Shou Sugi Ban timber cladding.\nHeat Source: NIBE Air-to-Water inverter heat pump.\nWindows: Schüco triple-pane aluminum (Uw = 0.78 W/m²K).",
    3: "M6 Budget Breakdown:\nTotal Allocated: €220,000 | Spent to date: €98,500\nKey Contractors: Nordic Build AS, Thermic Flow AS, Volta Tech AS.",
    4: "M6 Master Timeline:\nPhase 1: Permits & Demolition (Done)\nPhase 2: Envelope & Roofing (Done)\nPhase 3: Technical & Floor Heating (In Progress)\nPhase 4: Interior & Kitchen (Planned)"
  };

  const text = sourceTexts[sourceId] || "";
  navigator.clipboard.writeText(text).then(() => {
    showToast(`Source 0${sourceId} text copied to clipboard!`);
  });
}

// Copy NotebookLM Prompt
function copyPrompt() {
  const prompt = document.getElementById('promptText').innerText;
  navigator.clipboard.writeText(prompt).then(() => {
    showToast("NotebookLM prompt copied!");
  });
}

// Modal Controls
function openNotebookModal() {
  document.getElementById('notebookModal').classList.add('active');
}

function closeNotebookModal() {
  document.getElementById('notebookModal').classList.remove('active');
}

// Toast Notifications
function showToast(message) {
  const toast = document.getElementById('toastNotification');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// Save Checklist state to LocalStorage
function saveProgress() {
  const floorChecked = document.getElementById('taskFloor')?.checked;
  const hrvChecked = document.getElementById('taskHrv')?.checked;
  localStorage.setItem('m6_task_floor', floorChecked);
  localStorage.setItem('m6_task_hrv', hrvChecked);
  showToast("Progress saved!");
}

function loadProgress() {
  const floorChecked = localStorage.getItem('m6_task_floor') === 'true';
  const hrvChecked = localStorage.getItem('m6_task_hrv') === 'true';
  if (document.getElementById('taskFloor')) document.getElementById('taskFloor').checked = floorChecked;
  if (document.getElementById('taskHrv')) document.getElementById('taskHrv').checked = hrvChecked;
}

// On Page Load
document.addEventListener('DOMContentLoaded', () => {
  initSlider();
  loadProgress();
});

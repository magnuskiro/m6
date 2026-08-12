// M6 Fornyelse - Interaktiv Applikasjonslogikk

// Romdata og Beskrivelser
const roomsData = {
  exterior: {
    title: 'Fasade & Utvendig Transformasjon',
    details: 'Erstatning av slitt 1974-trekledning med Shou Sugi Ban brent tre, montering av trelags Schüco skyvedører, båndtekket metalltak og integrert varm arkitektonisk utebelysning.',
    status: 'Klimaskall Fullført',
    statusClass: 'status-completed',
    beforeImg: 'assets/images/exterior_before.jpg',
    afterImg: 'assets/images/exterior_after.jpg'
  },
  living: {
    title: 'Åpen Stue & Allrom (65 m²)',
    details: 'Fjerning av 1974-stendervegger for å utvide stuearealet, montering av HEB 220 bærende ståldrager (R 60 brannbeskyttet), hvitoljet eikeparkett, betongpeis og innfelt LED-cove i himling.',
    status: 'Gjenstår Overflater',
    statusClass: 'status-progress',
    beforeImg: 'assets/images/living_before.jpg',
    afterImg: 'assets/images/living_after.jpg'
  },
  kitchen: {
    title: 'Kjøkken & Marmorøy',
    details: 'Utrensing av opprinnelige 1970-talls laminatskap, erstattet med mørke mattedører, hvit eikefinish, 3,2m marmorøy med nedfelling, Gaggenau hvitevarer og integrert benkevifte.',
    status: 'Kjøkken Bestilt',
    statusClass: 'status-progress',
    beforeImg: 'assets/images/kitchen_before.jpg',
    afterImg: 'assets/images/kitchen_after.jpg'
  },
  bathroom: {
    title: 'Hovedbad & Badstue',
    details: 'Transformasjon av datert bad til minimalistisk spabad med italienske storformat porselensfliser, mikrosementvegger, innbygde armaturer, regndusj, frittstående kar og integrert sedertre-badstue.',
    status: 'Rørlegger Pågår',
    statusClass: 'status-progress',
    beforeImg: 'assets/images/living_before.jpg',
    afterImg: 'assets/images/living_after.jpg'
  }
};

let currentRoom = 'exterior';
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

// Bytte Valgt Rom
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

// Kopiere NotebookLM Kildeliste
function copySourceContent(sourceId) {
  const sourceTexts = {
    1: "M6 Fornyelse - Prosjektoversikt\nAdresse: Myrteveien 6, Tolvsrød (Gnr 140 / Bnr 371)\nMål: Transformere 1974-boligen til en modernisert skandinavisk arkitektbolig med TEK17 energispesifikasjoner.",
    2: "M6 Tekniske Spesifikasjoner:\nVeggisolering: 200mm Rockwool utvendig + Shou Sugi Ban brent trekledning.\nVarmekilde: NIBE Luft-til-vann inverter varmepumpe.\nVinduer: Schüco 3-lags lavenergiglass (Uw = 0,78 W/m²K).",
    3: "M6 Budsjettfordeling:\nAvsatt Budsjett: kr 2 500 000 | Påløpt til nå: kr 1 150 000\nHovedleverandører: Nordic Build AS, Thermic Flow AS, Volta Tech AS.",
    4: "M6 Fremdriftsplan:\nFase 1: Byggesøknad & Riving (Fullført)\nFase 2: Båndtekking & Klimaskall (Fullført)\nFase 3: VVS, Varmepumpe & Gulvvarme (Pågår)\nFase 4: Innvendig Eikeparkett & Kjøkkenøy (Planlagt)",
    5: "M6 Anbefalt 9-Trinns Byggerekkefølge:\nTrinn 1: Byggesøknad & Rigging\nTrinn 2: Utrensing & Riving\nTrinn 3: Kjeller, Drenering & Radon\nTrinn 4: Ståldrager HEB 220 (R 60)\nTrinn 5: Tett Bygg (EI 60)\nTrinn 6: Tekniske Føringer (Elektro, PEX, Varmepumpe)\nTrinn 7: Dampsperre & Gipsing (Q4)\nTrinn 8: Våtrom (BVN) & Eikeparkett\nTrinn 9: Innregulering & Ferdigattest",
    6: "M6 Tønsberg Kommuneplan 2023-2035 Bestemmelser:\nPlanID: 3803 99010 (Vedtatt 03.04.2024)\n%BYA: Maks 25 % BYA (M6 planlagt: 21,5 % BYA inkl 18m² biloppstilling)\nHøydegrenser: Maks 9,0m møne / 6,5m gesims\nNabogrense: Min. 4,0m avstand (PBL § 29-4)\nOvervann: LOD 3-trinnsstrategi (Stenkiste/infiltrering)",
    7: "M6 Tønsberg Arkitekturhåndbok (PBL § 29-2 Estetikk):\nMaterialitet: Shou Sugi Ban brent tre + Ruukki mattsvart båndtekket tak\nSolceller: Planmonterte solceller på tak fluktende med takflate tilfredsstiller automatiske visuelle krav\nUtendørs belysning: Avskjermede LED-spotter med varm fargetemperatur (2700K-3000K)"
  };

  const text = sourceTexts[sourceId] || "";
  navigator.clipboard.writeText(text).then(() => {
    showToast(`Kilde 0${sourceId} kopiert til utklippstavlen!`);
  });
}

// Kopiere Prompt
function copyPrompt() {
  const promptEl = document.getElementById('promptText');
  if (!promptEl) return;
  navigator.clipboard.writeText(promptEl.innerText).then(() => {
    showToast("NotebookLM prompt kopiert!");
  });
}

// Modal Kontroller
function openNotebookModal() {
  const modal = document.getElementById('notebookModal');
  if (modal) modal.classList.add('active');
}

function closeNotebookModal() {
  const modal = document.getElementById('notebookModal');
  if (modal) modal.classList.remove('active');
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

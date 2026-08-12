# 🏠 M6 Renew - House Total Rehabilitation Project

Welcome to **M6 Renew**, the central repository and interactive planning hub for the total house rehabilitation and architectural overhaul of the **M6 Residence**.

[![NotebookLM Connected](https://img.shields.io/badge/NotebookLM-m6--renew-blue?style=for-the-badge&logo=google)](https://notebooklm.google.com/)
[![License](https://img.shields.io/badge/Status-In%20Progress-emerald?style=for-the-badge)](#)

---

## 📌 Project Overview & Purpose
The purpose of this project is to plan, track, manage, and visually document the complete rehabilitation of an original residential house (designed in 1946, built in 1947) into a state-of-the-art, high-efficiency Scandinavian dwelling.

### Key Objectives:
- 🏗️ **Structural Open-Concept Overhaul**: Removing non-bearing walls and installing steel support beams (HEB 220) to create a unified 65 m² living and kitchen area.
- ⚡ **Zero-Net Ready Energy Upgrade**: 200mm exterior Rockwool insulation, Shou Sugi Ban vertical timber cladding, standing seam metal roof with 12.8 kWp solar PV array.
- ♨️ **Modern HVAC Systems**: NIBE Air-to-Water heat pump paired with hydronic floor heating across all levels and a high-efficiency heat recovery ventilation (HRV) unit.
- 📱 **AI-Driven Project Planning**: Direct integration with Google **NotebookLM** ("m6 - renew") to synthesize contractor quotes, structural blueprints, and material specifications into actionable AI insights.

---

## 🌟 Interactive Before & After Web Application
This repository includes a dynamic visual web application (`index.html`) featuring:
1. **Split-Screen Interactive Image Slider**: Compare vintage 1947 before states with 2026 architectural target renders across multiple zones (Exterior facade, Living room, Kitchen, Master bathroom).
2. **Master Renovation Roadmap**: Interactive phase timeline tracking completion from permits to final inspection.
3. **NotebookLM Integration Panel**: Quick access to Markdown source exports, suggested prompts, and audio summary helpers.
4. **Live Budget & Expense Tracker**: Category-by-category breakdown of allocated budget (€220,000) vs actual spending (€98,500).

---

## 🔗 NotebookLM Project Integration
This project is connected to the **"m6 - renew"** NotebookLM project workspace.

The `notebooklm/sources/` directory contains structured, AI-ready source documentation:
- 📄 [`01_PROJECT_OVERVIEW.md`](notebooklm/sources/01_PROJECT_OVERVIEW.md): Executive summary, scope of work by room, building dimensions.
- 📄 [`02_TECHNICAL_SPECIFICATIONS.md`](notebooklm/sources/02_TECHNICAL_SPECIFICATIONS.md): U-values, HVAC models (NIBE, Systemair), electrical setup, window specs (Schüco Ug 0.5).
- 📄 [`03_BUDGET_AND_CONTRACTORS.md`](notebooklm/sources/03_BUDGET_AND_CONTRACTORS.md): Itemized financial tracker and master contractor registry.
- 📄 [`04_RENOVATION_TIMELINE.md`](notebooklm/sources/04_RENOVATION_TIMELINE.md): 5-phase schedule and milestone checklist.

For full setup instructions, see [NOTEBOOKLM.md](NOTEBOOKLM.md).

---

## 🌐 Running the Web Application Locally
You can launch a local HTTP development server to view and interact with the webpage:

```bash
# Using Python builtin server
python3 -m http.server 8080

# Or using npx http-server
npx http-server -p 8080
```

Open `http://localhost:8080` in your browser.

---

## 📁 Repository Structure
```
m6/
├── index.html                   # Interactive Web Application
├── styles.css                   # Custom Glassmorphism & Dark Theme CSS
├── app.js                       # Slider Drag & Interactive JS Engine
├── NOTEBOOKLM.md                # NotebookLM Integration Guide
├── README.md                    # Main Project Documentation
├── assets/
│   └── images/                  # Before & After High-Res Renders
│       ├── exterior_before.jpg
│       ├── exterior_after.jpg
│       ├── living_before.jpg
│       ├── living_after.jpg
│       ├── kitchen_before.jpg
│       └── kitchen_after.jpg
└── notebooklm/
    └── sources/                 # Markdown context sources for NotebookLM
        ├── 01_PROJECT_OVERVIEW.md
        ├── 02_TECHNICAL_SPECIFICATIONS.md
        ├── 03_BUDGET_AND_CONTRACTORS.md
        └── 04_RENOVATION_TIMELINE.md
```

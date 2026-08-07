# M6 Renew - NotebookLM Integration Guide

Welcome to the **m6 - renew** NotebookLM project connector.

## Overview
NotebookLM is Google's AI notebook powered by Gemini. By connecting this repository to your **"m6 - renew"** NotebookLM project, you get a dedicated AI assistant that has full context of your house rehabilitation specs, structural plans, contractor quotes, and standard building sequence guidelines.

---

## 🔗 How to Connect with NotebookLM ("m6 - renew")

1. **Open NotebookLM**:
   Navigate to [NotebookLM](https://notebooklm.google.com/) and open or create your project titled **"m6 - renew"**.

2. **Import Sources**:
   Upload the curated markdown files inside the `notebooklm/sources/` directory:
   - 📄 [`01_PROJECT_OVERVIEW.md`](notebooklm/sources/01_PROJECT_OVERVIEW.md) - House background, architectural vision, total scope.
   - 📄 [`02_TECHNICAL_SPECIFICATIONS.md`](notebooklm/sources/02_TECHNICAL_SPECIFICATIONS.md) - Insulation specs, heat pump (TEK17/Passivhaus targets), electrical & plumbing.
   - 📄 [`03_BUDGET_AND_CONTRACTORS.md`](notebooklm/sources/03_BUDGET_AND_CONTRACTORS.md) - Detailed budget, cost tracking, supplier quotes.
   - 📄 [`04_RENOVATION_TIMELINE.md`](notebooklm/sources/04_RENOVATION_TIMELINE.md) - Phase milestones, schedule & dependencies.
   - 📄 [`05_BUILDING_SEQUENCE.md`](notebooklm/sources/05_BUILDING_SEQUENCE.md) - Standard & recommended 9-stage building sequence and technical order.

3. **Recommended NotebookLM Prompts**:
   - *"Explain the recommended 9-stage building sequence for M6 and why stage 5 weather-tightness is required before stage 6 technical rough-in."*
   - *"Summarize the current technical risks and thermal insulation gaps for the M6 renovation."*
   - *"Create a weekly checklist for Phase 3: HVAC, Floor Heating, and Technical utilities."*
   - *"Draft an email to the contractor asking about heat pump delivery dates and total quote variance."*

---

## 🚀 Live Dashboard Integration
The interactive dashboard in `index.html` features a **NotebookLM Sync Panel** that allows you to copy pre-formatted source summaries or prompt templates directly into your NotebookLM workflow!

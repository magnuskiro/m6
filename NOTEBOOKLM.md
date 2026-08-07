# M6 Renew - NotebookLM Integration Guide

Welcome to the **m6 - renew** NotebookLM project connector.

## Overview
NotebookLM is Google's AI notebook powered by Gemini. By connecting this repository to your **"m6 - renew"** NotebookLM project, you get a dedicated AI assistant that has full context of your house rehabilitation specs, structural plans, contractor quotes, and material lists.

---

## 🔗 How to Connect with NotebookLM ("m6 - renew")

1. **Open NotebookLM**:
   Navigate to [NotebookLM](https://notebooklm.google.com/) and open or create your project titled **"m6 - renew"**.

2. **Import Sources**:
   Upload the curated markdown files inside the `notebooklm/sources/` directory:
   - 📄 [`01_PROJECT_OVERVIEW.md`](file:///home/kiro/repos/m6-renew/notebooklm/sources/01_PROJECT_OVERVIEW.md) - House background, architectural vision, total scope.
   - 📄 [`02_TECHNICAL_SPECIFICATIONS.md`](file:///home/kiro/repos/m6-renew/notebooklm/sources/02_TECHNICAL_SPECIFICATIONS.md) - Insulation specs, heat pump (TEK17/Passivhaus targets), electrical & plumbing.
   - 📄 [`03_BUDGET_AND_CONTRACTORS.md`](file:///home/kiro/repos/m6-renew/notebooklm/sources/03_BUDGET_AND_CONTRACTORS.md) - Detailed budget, cost tracking, supplier quotes.
   - 📄 [`04_RENOVATION_TIMELINE.md`](file:///home/kiro/repos/m6-renew/notebooklm/sources/04_RENOVATION_TIMELINE.md) - Phase milestones, schedule & dependencies.

3. **Recommended NotebookLM Prompts**:
   - *"Summarize the current technical risks and thermal insulation gaps for the M6 renovation."*
   - *"Create a weekly checklist for Phase 2: Electrical & Structural demolition."*
   - *"Draft an email to the contractor asking about heat pump delivery dates and total quote variance."*
   - *"Generate an Audio Overview explaining the M6 rehabilitation vision for family members."*

---

## 🚀 Live Dashboard Integration
The interactive dashboard in `index.html` features a **NotebookLM Sync Panel** that allows you to copy pre-formatted source summaries or prompt templates directly into your NotebookLM workflow!

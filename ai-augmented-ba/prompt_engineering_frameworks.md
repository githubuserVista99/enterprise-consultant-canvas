# Enterprise AI-Augmented Project Delivery & Prompt Engineering System

This document outlines the formal prompt engineering framework used to accelerate Agile requirements management, backlog grooming, and functional system specifications delivery using LLM models (ChatGPT, Anthropic Claude).

---

## 🤖 1. System Requirement Synthesis Prompt (The Epics-to-Stories Generator)
* **Objective:** Transforms highly unstructured stakeholder meeting raw notes or legacy ERP outlines directly into structured, engineering-ready Agile user stories with clear boundaries.

```text
[SYSTEM ROLE]: Elite Technical IT Product Owner and Database System Analyst.
[CONTEXT]: I am consolidating multiple fragmented databases (MySQL, SQL Server) and SAP BW cubes into a central Cloud Data Warehouse.
[INPUT]: The stakeholder notes provided below are messy and lack technical metrics.
[OBJECTIVE]: Extract the explicit functional requirements and generate a structured list of Agile User Stories in the standard 'As a... I want to... So that...' format. For each story, define rigorous, technical "Acceptance Criteria" including performance targets (e.g., target latency under 2 seconds, indexing strategy constraints).

[STAKEHOLDER NOTES]:
"We need to pull financial reports quickly. Right now, the sales reports take 20 minutes to load because they grab data live from both our old MySQL web store database and our regional SQL Server node. The accountant needs to see yesterday's gross figures by 6:00 AM every day without lagging out the live transactional checkout servers."
```

---

## 📊 2. AI-Assisted "Vibe Coding" & Prototyping Workflow
By pairing prompt engineering with modern code tools (GitHub Copilot), complex database migration or indexing scripts can be prototyped rapidly with guardrails:

1. **Context Context Gathering:** Use custom scripts to fetch data dictionaries and constraint metrics from system tables.
2. **Deterministic Structuring:** Instruct the AI engine to generate code utilizing ANSI SQL standards to prevent compatibility drift across platforms.
3. **Rigorous Validation Iterations:** Pass generated schemas directly through localized staging test loops to catch performance regression errors before production commits.

# Planning Updates – Alignment with Research Synthesis
*(Generated 2025‑04‑22)*

---
## Overview
This checklist details **exact actions** required to reconcile GitHub Issues & Project Boards with the new enhancement roadmap (A1–A7) and micro‑service recommendation. Execute steps top‑down; each sub‑task references the repository or project board it affects.

> **Context Note :** You are a solo developer working alongside AI coding agents. The steps below assume no human team‑mates and optimize for automation over meetings.

Legend: 🔹 new issue ✏️ update issue/label 📌 board action ✅ close/merge duplicate

---
## 1 Global Actions
|Step|Action|
|----|------|
|G‑1| 📌 Add **Blocked (Security)** column to **Trading System Development** board|
|G‑2| 📌 Add field **“Recommendation Ref”** (text) to both boards; store ID (e.g., `A1`) for traceability|
|G‑3| ✏️ Re‑label any open issue containing “Task X” with proper semantic prefixes (`feat`, `chore`, `docs`, etc.)|
|G‑4| ✅ Close duplicate numbered tasks in *trade‑discovery* (#10 vs #5, #11 vs #6) keeping the lower number|

---
## 2 airflow‑hub (repo)
|Step|Task|Details|
|----|----|-------|
|AH‑1| 🔹 `feat: Implement secrets vault & Airflow Connections (A1)`|Labels: `security`, `high‑priority`|
|AH‑2| 🔹 `chore: Add Airflow pools & API rate‑limit guards (A4)`|Attach to **Airflow Integration** board → `Backlog`|
|AH‑3| 🔹 `test: DAG validation & unit tests (A4)`|Labels: `testing`|
|AH‑4| ✏️ Issue #6 “Documentation & Status Refresh” → add `architecture` label and link to Rec A5 (dependency split)|
|AH‑5| 📌 Move AH‑1 & AH‑2 to **Blocked (Security)** until Vault base setup (TM‑1) complete|

---
## 3 market‑analysis (repo)
|Step|Task|Details|
|----|----|-------|
|MA‑1| 🔹 `feat: Externalise data‑source API creds via Vault (A1)`|Add to Trading board → `Backlog`|
|MA‑2| 🔹 `feat: Add Prometheus exporter & dashboards (A6)`|Labels: `monitoring`|
|MA‑3| ✏️ Issue #6 “Set up monitoring” → rename to “Implement Prometheus metrics (A6)” and mark **in‑progress**|
|MA‑4| ✏️ Issue #7 “Implement backtesting” → add `simulation` label (ties to A7)|

---
## 4 trade‑manager (repo)
|Step|Task|Details|
|----|----|-------|
|TM‑1| 🔹 `feat: Add ib‑gateway container & adapter refactor (A2)`|Labels: `broker`, `high‑priority`; assign to you|
|TM‑2| 🔹 `feat: Add SIMULATION_MODE flag & paper trading config (A7)`|Labels: `simulation`|
|TM‑3| ✏️ Issue #6 “Set up monitoring” → scope to Prometheus stack (link A6)|
|TM‑4| 📌 Place TM‑1 under **Blocked (Security)** until AH‑1 completes (dependency)|

---
## 5 trade‑discovery (repo)
|Step|Task|Details|
|----|----|-------|
|TD‑1| 🔹 `refactor: Remove internal scheduler & integrate Airflow dynamic task‑mapping (A3)`|Labels: `architecture`|
|TD‑2| ✅ Close duplicates (#10 vs #5, #11 vs #6) → keep lower numbers|
|TD‑3| ✏️ Issue #11 now points to TD‑1 (link Rec A3) and relabel as `in‑progress` once started|

---
## 6 trade‑dashboard (repo)
|Step|Task|Details|
|----|----|-------|
|TDash‑1| 🔹 `chore: Integrate global Traefik ingress in Compose (Micro‑service Rec)`|Labels: `architecture`, `low‑priority`|
|TDash‑2| ✏️ Issue #1 “Implement Secure Microservices Architecture” → narrow scope to frontend impact; link to Traefik task; remove duplicate labels|

---
## 7 Project Board Item Mapping
|Board|Add Item|Move to Column|
|-----|--------|--------------|
|Airflow Integration|AH‑1, AH‑2, AH‑3, TD‑1|`Backlog`|
|Trading System Development|TM‑1, TM‑2, MA‑1, MA‑2, MA‑3, TDash‑1|`Backlog`|

---
## 8 Automation & Follow‑up
1. Configure **GitHub Actions** workflow to auto‑add issues with label `high‑priority` to the top of each board.
2. Create a scheduled GitHub Action (or local cron + AI script) that flags any card in **Blocked (Security)** for more than 24 hours, prompting the AI agent to unblock or re‑prioritise.

---
### End of checklist

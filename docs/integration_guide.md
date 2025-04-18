# Airflow-Hub Integration Guide

Welcome to **airflow-hub**, our central Airflow monorepo. This document explains how external projects 
(e.g., trading repos, git-books, or future apps) can be adapted to run under Airflow.

---

## 1. Scope and Principles

1. **Single Airflow Instance**  
   - `airflow-hub` runs one Airflow environment for orchestrating a variety of projects.
   - DAGs for each project live under `dags/` in subfolders matching the project’s name.

2. **Evolving Projects**  
   - None of the external projects are fully operational yet; *it’s perfectly acceptable* to modify or restructure 
     existing code so it fits Airflow’s best practices.
   - The AI or any contributor may reorganize modules, rename functions, and introduce new files or operators
     as needed to make them “Airflow-ready.”

3. **Future Growth**  
   - Additional or dissimilar projects can be integrated without needing multiple Airflow instances, 
     so long as we follow consistent naming, modular code, and best practices.

---

## 2. Repository Layout Overview

Below is a simplified structure of `airflow-hub`. New subfolders can be created for additional projects as needed.

``` plaintext
airflow-hub/
├── dags/
│   ├── market-analysis/
│   ├── trade-discovery/
│   ├── trade-dashboard/
│   ├── trade-manager/
│   ├── git-books/
│   └── …
├── plugins/
│   ├── common/            # Reusable hooks/operators used by multiple projects
│   ├── market-analysis/    # If needed for specialized code
│   ├── trade-discovery/
│   ├── …
│   └── git-books/
├── tests/
│   ├── common/
│   ├── market-analysis/
│   ├── …
│   └── test_dag_validation.py
├── requirements.txt        # Shared dependencies
├── Dockerfile             # If we containerize Airflow
└── DOCS/
└── INTEGRATION_GUIDE.md  # (This file)
```

---

## 3. How to Integrate an External Project

1. **Add or Adjust Code for Airflow Tasks**  
   - Identify scripts, modules, or classes in your external repo that should be scheduled or orchestrated 
     by Airflow.  
   - If these scripts need to be reorganized (e.g., function-based rather than a single monolithic `main()`), 
     **feel free** to do so. Airflow typically references Python callables or custom operators.

2. **Create a Corresponding DAG**  
   - In `airflow-hub`, under `dags/<project_name>/`, create one or more DAG files 
     (e.g., `dag_market_analysis_ingestion.py`).  
   - The DAGs typically import your project’s logic (either by referencing a local copy or 
     pulling from a separate environment if you prefer).  
   - Keep DAG definitions declarative (schedules, tasks, dependencies), while business logic 
     resides in **plugins** or in your external repo’s modules.

3. **Shared vs. Project-Specific Code**  
   - If multiple projects can benefit from the same logic (e.g., a utility to read config from S3), 
     place it in `plugins/common/`.  
   - For code unique to one project, put it in `plugins/<project_name>/`.  
   - DAG files in `dags/<project_name>/` should import from these plugin modules or from your external repo.

4. **Dependencies & Execution Environment**

   When integrating code from external projects, managing dependencies and the execution environment is crucial. **The standard and mandated approach for this monorepo is to use containerized tasks.**

   - **Mandated Approach: Containerized Tasks (Docker)**
     - **Why?** This provides the best isolation, preventing dependency conflicts between different projects (e.g., `git-books` needing a different library version than `trade-manager`). Each project runs in its own controlled environment.
     - **How?**
       - Each external project repository (e.g., `git-books`, `market-analysis`) **MUST** include a `Dockerfile`.
       - This `Dockerfile` should define the environment needed to run its tasks, including:
         - A suitable base image (e.g., a specific Python version).
         - Copying necessary project code into the image.
         - Installing all required dependencies (e.g., via `pip install -r requirements.txt` within the Docker build process).
       - In the `airflow-hub` DAGs, you will use the `airflow.providers.docker.operators.docker.DockerOperator`.
       - The `DockerOperator` will be configured to run a command inside a container built from the project's specific Docker image.
     - **Benefits:** Complete dependency isolation, consistent environments, flexibility in using different tools/versions per project.

   - **Alternative (Discouraged for External Projects): Shared Environment**
     - Adding dependencies directly to `airflow-hub`'s central `requirements.txt` is **strongly discouraged** for integrating external projects due to the high risk of conflicts.
     - This approach *might* be acceptable *only* for very simple, self-contained utility scripts developed *within* `airflow-hub` itself, with minimal dependencies.

   **Decision:** For all integrations involving code originating from repositories outside `airflow-hub` (like `git-books`, `trade-dashboard`, etc.), **you MUST use the Containerized Tasks (Docker) approach.**

5. **Secrets Management**  
   - Store secrets in Airflow connections or external secrets backends.  
   - Never commit credentials in code—reference them by ID (e.g., `conn_id='trade_manager_ibkr'`).

6. **Testing & CI**  
   - The `test_dag_validation.py` ensures that each DAG can be parsed by Airflow.  
   - Add or update unit tests in the `tests/<project_name>/` directory for any custom logic.

---

## 4. Per-Project Instructions

Each external repo should have a local `AIRFLOW_INTEGRATION.md` explaining:
1. Which scripts or modules are candidate tasks.  
2. Any reorganization that might be needed for them to work as DAG tasks.  
3. The location or name of the DAG(s) in `airflow-hub` referencing that code.  

See below for an example you can copy into each project.

---

## Links to External Repos

Below are the known external project repos slated for integration:

- **Trading System**  
  1. [market-analysis](https://github.com/mprestonsparks/market-analysis)  
  2. [trade-discovery](https://github.com/mprestonsparks/trade-discovery)  
  3. [trade-dashboard](https://github.com/mprestonsparks/trade-dashboard)  
  4. [trade-manager](https://github.com/mprestonsparks/trade-manager)

- **git-books**  
  - [git-books](https://github.com/mprestonsparks/git-books)

Future or dissimilar repos can be integrated following the same steps outlined here.
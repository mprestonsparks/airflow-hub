# Gap Analysis – Airflow Integration (2025‑04‑21)

**Generated:** 2025‑04‑21 13:47‑05:00  
**airflow‑hub commit:** dd5932e3  
**market‑analysis commit:** 000958d6

This document records the discrepancies between our planning documents and the currently‑committed code for the Airflow monorepo plus the first integrated external repo (`market‑analysis`).  Use it as a living reference while closing the remaining gaps.

---

## 1  Summary of Findings

*   The overall repository structure matches the architecture guide, but several “next” repos (trade‑manager, trade‑discovery, trade‑dashboard, git‑books) are still missing DAG folders and Docker images.
*   `market‑analysis` is largely integrated and uses the mandated `DockerOperator`, but trading DAGs still execute Python directly inside the Airflow image, violating the isolation rule.
*   CI / lint / coverage pipelines are absent across all repos; documentation claims they should be present.
*   Secrets / connection bootstrap and pool creation are undocumented and unscripted.
*   Task‑matrix & status YAML files are out of date and give the false impression that no work has started.

See Section 2 for a full table of gaps.

---

## 2  Detailed Gap Table

| Area | Requirement (earliest docs) | Current Code | Gap / Action |
|------|-----------------------------|--------------|--------------|
| Containerised tasks for **all** external code | Must use `DockerOperator` | `market‑analysis` ✔, Trading DAG ❌ | Containerise IBKR extract or move deps into image |
| Task matrix accuracy | Should reflect real state | All ⬜ | Update matrix & status files |
| CI / lint / test pipeline | GitHub Actions (pytest + flake8) | Absent | Add minimal CI workflow |
| Secrets / pools bootstrap | Scripted or IaC | Absent | Create `scripts/bootstrap_airflow.py` |
| Dependency pinning | Exact versions | Loose `>=` versions | Adopt pip‑tools / pin reqs |
| RBAC and monitoring | Documented + implemented | Not implemented | Plan Prom/Grafana + Airflow roles |

---

## 3  Immediate Next Steps (ordered)

1. **Documentation & status refresh** – update task matrix, status YAML, create repo issues.
2. **Minimal CI pipeline** – pytest + flake8 + `airflow dags list` in docker‑compose.
3. **Containerise trading extract step** – move IBKR dependencies into dedicated image and replace Python operator with `DockerOperator`.
4. **Bootstrap script for connections & pools** – automate creation of Airflow connections (`market_analysis_ibkr`, etc.).
5. **Dependency pinning strategy** – introduce `pip‑tools` and lock files.
6. **Prepare integration stubs** – create `AIRFLOW_INTEGRATION.md` + Dockerfiles for `trade‑manager`, `trade‑discovery`, `trade‑dashboard`.

These items will be tackled sequentially and reflected in the project board.

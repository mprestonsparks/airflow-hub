# 2025-04-25 Airflow-Hub **Final Execution Plan**

> **Purpose**  Provide an end-to-end, _actionable_ blueprint that merges every requirement from
> • `2025-04-25_airflow-hub_refactor_context.md`
> • `(2025-04-23) DAG_RESTRUCTURE_PLAN.md`
> • other repo docs (INSTRUCTIONS.md, README, Docker files…)
> into **one conflict-free roadmap**.  After sign-off we will execute this plan verbatim
> and verify completion with the metrics listed in § 7.

---
## 1  Decision hierarchy (UPDATED)
1. **Live repository state** – the actual functioning code in `airflow-hub/`, `market-analysis/`, etc.
2. **Most-recent strategic context docs** – specifically `2025-04-25_airflow-hub_refactor_context.md` **and this execution plan**. These embody the latest research and override any earlier roadmap when conflicts appear.
3. **Older repository design docs** – e.g. `DAG_RESTRUCTURE_PLAN.md`, `INSTRUCTIONS.md`, legacy TODO files.  _Warning:_ these documents may describe **deprecated structures or plans**. Use them for background and vocabulary, but **do not treat them as authoritative requirements** without cross-checking against § 1-2 above.
4. **Industry best practice & engineering judgement** – Airflow ≥2.7 conventions, Helm chart defaults, TaskFlow API patterns, etc.
5. **Conversation transcripts / miscellaneous notes** – helpful for rationale; never override higher sources.

> **Why this matters**  Earlier planning documents remain valuable but could contain obsolete instructions.  By explicitly lowering their priority _and_ documenting this caveat, we prevent future contributors (human or AI) from inadvertently resurrecting outdated patterns.

---
## 2  Scope & Objectives
✔ Convert to **function-first folders** (`dags/{ingestion,execution,transformation,analytics}`)
✔ Enforce **`provider[_asset]` ⇒ *domain* ontology** for _both_ filenames and DAG IDs.
✔ Generate workflows **declaratively via [`dag-factory`](https://github.com/astronomer/dag-factory)** (one generator → many YAML definitions).
✔ Replace legacy **SubDAGs → TaskGroups**.
✔ Maintain **multi-tenant isolation** (namespaced pools, connections, variables).
✔ 100 % **open-source deployability** (Docker Compose dev; optional Helm→K8s prod).
✔ Ship **CI pipelines** (lint, tests, DAG import) + docs kept in sync.

_No vague items remain—every objective is satisfied by explicit steps below._

---
## 3  High-level folder layout (post-migration)
```
airflow-hub/
├─ dags/
│  ├─ ingestion/
│  ├─ execution/
│  ├─ transformation/
│  └─ analytics/
├─ plugins/
│  ├─ shared/            # docker_op defaults, helpers
│  └─ taskgroups/        # reusable TaskGroup factories
├─ tests/                # pytest suite inc. DAG import test
├─ docker/
└─ docs/
```
Every file inside a domain obeys `<provider>[_<asset>]_ <domain>.yaml` (or _.py_ for code-heavy DAGs).

---
## 4  Execution phases (chronological)

| # | Phase | Key actions | Blocking? |
|---|-------|-------------|-----------|
|0| **Safety net** | `git checkout -b feat/ontology-refactor` • dump meta DB | ✔ |
|1| **Deps** | Add `dag-factory~=1.4`, `pyyaml~=6.0` to `requirements/base.txt`; `pip install` | ✔ |
|2| **Folder skeleton** | `mkdir -p dags/{ingestion,execution,transformation,analytics}`; purge `dags/project_*`, `dags/configs/` | ✔ |
|3| **Core DAG factory** | `plugins/core_dag_factory.py` scans all domain dirs for `*.y*ml`, validates filename regex, then `DagFactory(cfg).generate_dags(globals())` | ✔ |
|4| **Inventory & rename script** | `scripts/inventory_rename.py` implements § 2 of *DAG_RESTRUCTURE_PLAN.md*; consults `migration/overrides.py`; performs `git mv`, rewrites `dag_id`, updates docs/tests | ✔ |
|5| **YAML conversion** | For each renamed DAG build YAML with same default_args, schedule, params.  Example template provided in Appendix A. | ✔ |
|6| **Shared helpers** | `plugins/shared/docker_defaults.py` ⇒ `def docker_task(**overrides)`; `plugins/taskgroups/ingestion.py` ⇒ `def batch_ingest(symbols, image, **docker_kwargs)` | ⧗ |
|7| **Multi-tenancy glue** |  • Prefix pools/vars/conns with `<provider>_`  • add RBAC roles mapping (`scripts/rbac_seed.py`)  • ensure secrets **only** via env or external back-end | ⧗ |
|8| **Tests + CI** | `tests/test_dag_import.py` (DagBag import), `pytest-airflow`, `flake8`, `black --check`; GH Actions workflow `.github/workflows/ci.yml` | ✔ |
|9| **Docker Compose tweak** | Mount `dags/` & `plugins/`; env `AIRFLOW__CORE__LOAD_EXAMPLES=False`; optional `AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags` | ✔ |
|10| **Docs update** | README domain overviews; per-domain README with naming rules; architecture diagram; update `INSTRUCTIONS.md` env vars | ✔ |
|11| **Optional Helm** (future) | Helm values patch file (`deploy/helm/values-ontology.yaml`) to mount Git-synced DAGs & plugins; statsD/prometheus included. | ⧗ |

Legend  ✔ = blocking for merge  ⧗ = may run in parallel once deps ready.

---
## 5  Edge-case handling
*Use `migration/overrides.py`*
```python
MIGRATION_MANUAL_OVERRIDES = {
    "dags/legacy_crypto_ingest.py": {"provider": "kraken", "asset": "spot", "domain": "ingestion"},
}
```
The inventory script checks this dict before heuristic parsing.

---
## 6  Rollback & Disaster recovery
1. `git reset --hard $LAST_GOOD_COMMIT`
2. `psql -U airflow < backup_YYYY-MM-DD.sql`
3. Restore old Docker Compose.

---
## 7  Validation & success metrics
| Check | Command | Success criteria |
|-------|---------|------------------|
|**Dag import**| `pytest -q tests/test_dag_import.py` | `DagBag.import_errors == {}` |
|**Scheduler start**| `docker compose up -d && docker compose logs -f airflow-scheduler` | No `ImportError`, N DAGs parsed = YAML count |
|**Smoke test**| `airflow dags test binance_spot_ingestion 2025-04-24` | All tasks succeed | 
|**CI pipeline**| GH Actions status | Green ✔ |
|**Folder audit**| `find dags -maxdepth 2 -type f ! -name "*_*.yaml"` | _no output_ |
|**RBAC roles**| `airflow roles list` | Roles prefixed per provider present |

Plan considered **done** when every row above passes in dev **and** staging.

---
## Appendix A  – YAML template
```yaml
default_args:
  owner: data_team
  retries: 2
  retry_delay_sec: 300

dag:
  dag_id: binance_spot_ingestion   # == filename
  schedule_interval: "@daily"
  start_date: 2025-01-01
  catchup: false
  max_active_runs: 1
  tags: [ingestion, binance, spot]

tasks:
  pull_prices:
    operator: airflow.providers.docker.operators.docker.DockerOperator
    image: market-analysis:latest
    docker_conn_id: docker_default
    command: >-
      python -m src.main --exchange binance --symbol {{ params.symbol }} --date {{ ds }}
    params:
      symbol: BTCUSDT
    environment:
      BINANCE_API_KEY: '{{ var.value.binance_api_key }}'
      BINANCE_SECRET_KEY: '{{ var.value.binance_secret_key }}'
    pool: binance_market_data
```

---
### End of document

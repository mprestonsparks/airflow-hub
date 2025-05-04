# Synthesis of AI‑Generated Research & Enhancement Plan

*(Compiled 2025‑04‑22)*

---
## 1. Research Summary

| Theme | Key Findings (Consensus) | Divergent / Nuanced Points |
|-------|-------------------------|---------------------------|
|Micro‑service Architecture|All docs endorse strict separation of **Market Analysis**, **Trade Manager**, **Trade Discovery**, **Dashboard** and **Airflow Hub** in individual containers.|ChatGPT‑45 proposes **one** shared Docker‑Compose network; Perplexity #2 suggests optional migration to Kubernetes / AWS Batch for scale.|
|Broker Integration (IBKR & Binance)|Run **IB Gateway** (or IBeam) in an isolated container; use **ib‑insync** and **python‑binance/ccxt** in execution service; store credentials in Airflow Connections.|Perplexity #2 highlights IB’s recent crypto support → possibility to consolidate to a single broker; ChatGPT‑45 prefers separate adapters.|
|Airflow Orchestration|Use Airflow for *coarse‑grained* orchestration (data ingestion, hourly scans, model retraining). Employ **dynamic task‑mapping**, **pools** and **Local/Celery Executor**.|ChatGPT‑45 warns Airflow not suitable for sub‑minute latency; suggests hybrid internal async loops.|
|State‑Aware PCA Strategy|Market‑analysis repo’s PCA + clustering approach is mirrored by several OSS projects; considered state‑of‑the‑art for adaptive trading.|Perplexity #3 notes similar frameworks but stresses need for robust back‑testing and regime drift detection.|
|Security & Secrets|All sources require external secret management, least‑privilege containers, minimal port exposure.|None disagree; ChatGPT‑45 details binding services to localhost.|
|Testing & CI/CD|Linting, unit + integration + DAG validation tests mandatory; Git‑based CI/CD pipeline per repo.|Perplexity #2 emphasizes ML model pipelines plus feature store; ChatGPT‑45 focuses on simulation / paper trading environments.|

---
## 2. Critical Issues (Prioritised)

| # | Issue | Location / Component | Evidence | Impact |
|---|-------|----------------------|----------|--------|
|1|**Secrets in Code** – current repos store API keys in `.env.example` files; no vault integration|All services|All three research docs stress external secret stores|High (security) |
|2|**IB Gateway Container absent** – Trade Manager assumes local TWS|`trade-manager` brokers|ChatGPT‑45, Perplexity #2 broker patterns|High (blocks live trading) |
|3|**Mixed Scheduling** – Discovery service has internal asyncio loop *and* Airflow triggers|`trade-discovery` main loop|ChatGPT‑45 (dupe scheduling antipattern)|Medium (complex debugging) |
|4|**No Airflow Pools / Rate‑limit guards** for API calls|Airflow DAGs|All docs recommend pools & back‑off|Medium (API bans) |
|5|**Incomplete Test Coverage & DAG validation**|`tests/`|Docs push for DAG/unit tests & lint|Medium |
|6|**Single requirements.txt** causing dependency clashes|`airflow-hub` root|Research cites option for per‑service deps|Medium |
|7|**Missing Monitoring Stack** (Prometheus/Grafana)|Infra|Best‑practice sections on observability|Low |

---
## 3. Enhancement Recommendations

| Rec | Action | Rationale | Complexity | Expected Impact | Affected Areas |
|-----|--------|-----------|------------|-----------------|---------------|
|A1|Implement **HashiCorp Vault (dev) or Docker Secrets** with Airflow Connections for all broker & DB creds.|Meets security best practices; removes secrets from git.|Medium|High|All services, Airflow
|A2|Add **ib‑gateway** container & update `docker-compose.yml`; refactor `InteractiveBrokersAdapter` to connect via env vars `IB_HOST/PORT`. |Enables headless IB connection; aligns with patterns.|Low|High|trade-manager, infra
|A3|Refactor scheduling: move periodic loops to Airflow DAGs with **dynamic task mapping** & **pools**; retain internal async only for sub‑minute needs.|Single source of truth for schedule.|Medium|Medium|trade-discovery, airflow DAGs
|A4|Create **tests/** per repo: operator tests, DAG validation (`airflow dags test`), contract tests between services.|QA & regression safety.|High|High|all codebases
|A5|Split dependencies: maintain **base image** + per‑service `requirements.txt`; use slim images; leverage Docker build‑cache.|Avoids heavy Airflow image; resolves conflicts.|Medium|Medium|Dockerfiles, CI
|A6|Introduce **Prometheus + Grafana OSS stack** with exporters for Airflow & FastAPI metrics; 15‑day log retention.|Lightweight monitoring per user rules.|Medium|Medium|infra, compose
|A7|Add **simulation mode flag** across services; default to paper trading envs; integrate with CI e2e tests.|Safe dry‑runs; research highlight.|Low|Medium|trade-manager, discovery

---
## 4. Implementation Roadmap

1. **Security Foundation** (Week 1)
    1.1 A1 – Secrets vault & Airflow Connection migration
    1.2 Create GitHub issue; link to project board (*blocker for live trading*)
2. **Broker Connectivity** (Week 1‑2)
    2.1 A2 – IB Gateway container & adapter refactor
3. **Orchestration Consolidation** (Week 2‑3)
    3.1 A3 – Remove internal loops; add/modify DAGs with pools & rate‑limits
4. **Testing & CI/CD Hardening** (Week 3‑4)
    4.1 A4 – Add pytest suites, DAG validation, GitHub Actions workflow
5. **Dependency & Build Optimisation** (Week 4)
    5.1 A5 – Split requirements; rebuild images; update compose
6. **Observability Layer** (Week 5)
    6.1 A6 – Prometheus/Grafana docker‑compose additions; dashboards templates
7. **Simulation & Paper Trading Enhancements** (Week 5)
    7.1 A7 – Feature flag, integration tests

Dependencies: A1 precedes any live trading tasks; A2 depends on vault env vars; A3 depends on A1 for credentials in DAGs.

Short‑Term (≤1 month): A1‑A4.  Long‑Term (>1 month): A5‑A7 & potential Kubernetes migration.

---
## 5. Code Examples

### 5.1 IB Gateway in Docker‑Compose
```yaml
services:
  ib-gateway:
    image: ghcr.io/quantrocket/ib-gateway:10.23
    environment:
      TWS_USERID: "${IB_USER}"
      TWS_PASSWORD: "${IB_PASS}"
    ports: [4002:4002]  # gateway API port
  trade-manager:
    build: ./trade-manager
    environment:
      IB_HOST: ib-gateway
      IB_PORT: 4002
    depends_on: [ib-gateway]
```

### 5.2 Secure Secret Retrieval in Airflow DAG
```python
from airflow.decorators import dag, task
from airflow.models import Variable, Connection

@dag(schedule_interval="@hourly", start_date=datetime(2025,4,22), catchup=False)
def discover_assets():

    @task()
    def fetch_opportunities():
        conn = Connection.get_connection_from_secrets("binance_api")
        api_key, api_secret = conn.login, conn.password
        resp = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            headers={"X-MBX-APIKEY": api_key}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    fetch_opportunities()

discover_assets()
```

### 5.3 Dynamic Task Mapping with Pools
```python
symbols = Variable.get("watchlist", deserialize_json=True)

@task.pool("api_pool")
@task.map
def analyze_symbol(sym):
    return httpx.post(f"http://market-analysis:8000/analyze", json={"symbol": sym}).json()
```

### 5.4 Simulation Flag in Trade Manager
```python
SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

if SIM_MODE:
    broker = MockBroker()
else:
    broker = InteractiveBrokersAdapter(host=os.getenv("IB_HOST"), port=int(os.getenv("IB_PORT", 4002)))
```

---
### Notes on Non‑Applicable Recommendations
- Migrating to **Kubernetes** deemed over‑engineered for single‑user setup → revisit once concurrent users >1.
- Enterprise APM solutions rejected per cost optimisation rule; OSS stack suffices.

---
## Next Steps
1. Review & approve roadmap.
2. Create GitHub issues (linked to project board) corresponding to each recommendation.
3. Update any `.project/status/DEVELOPMENT_STATUS.yaml` once file is added to repo in future.

---
*End of document*

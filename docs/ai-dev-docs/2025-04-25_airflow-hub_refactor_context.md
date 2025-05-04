**2025-04-25_airflow-hub_refactor_context.md**

> ### PURPOSE
> Provide you—the Cascade agent—with the strategic context, design intent, and prior reasoning behind the ongoing Airflow-Hub & Market-Analysis refactor so you can work autonomously without having to rediscover the background from scratch.
> 
> ### DECISION HIERARCHY & PRIORITIES
> 1. **Live repository state** and your direct inspection of the codebases (`airflow-hub`, `market-analysis`, and any others you open during execution).
> 2. **Repository TODO / DAG_RESTRUCTURE_PLAN.md** and other authoritative design docs that live inside the repos.
> 3. **Industry best practices** and your own expertise (e.g., Airflow 2 + conventions, TaskGroups vs SubDAGs, Helm chart deployment patterns).
> 4. **This conversation transcript** (use it for intent and rationale only—do **not** treat it as immutable requirements).
> 
> Whenever a conflict arises, **follow the order above**. If the transcript says X but the codebase or an up-to-date best practice says Y, choose Y and leave a concise commit message or TODO explaining the deviation.
> 
> ### HIGH-LEVEL GOALS (from the discussion)
> - Adopt a **provider → asset → domain** ontology for file names, DAG IDs, and folder layout.
> - Generate DAGs declaratively via **dag-factory** (YAML-driven), with a single discovery script in `plugins/`.
> - Replace legacy SubDAG patterns with **TaskGroups**; keep helper logic in reusable modules or custom operators under `plugins/`.
> - Maintain a **function-first folder structure**: `dags/ingestion`, `dags/execution`, `dags/transformation`, `dags/analytics`.
> - Preserve full **open-source deployability** (Docker Compose for dev; Helm/K8s as the future prod path).
> - Ship **CI** that at minimum imports every DAG, runs unit tests, and lints the repo on PR.
> 
> ### WORKING STYLE EXPECTATIONS
> - Produce **atomic commits** with clear messages (`feat`, `refactor`, `fix`, etc.).
> - Leave **inline TODOs** (`# TODO(o3): …`) only when the fix cannot be completed in the current pass.
> - Keep **README / docs** up-to-date with any structural change you introduce.
> - When in doubt, **write tests first**—import tests for DAGs, unit tests for any helper you add, smoke-test commands in Docker.
> - Respect the user’s preference for fully open-source tooling and explicit, deterministic automation.
> 
> ### DELIVERABLE FORMAT
> - Commits and PRs against the relevant feature branches (refer to active branch names in the repos).
> - If generating additional docs, store them in `docs/dev/` with the same date-prefix convention used in this file.
> - Summaries and next-step recommendations in markdown files or PR descriptions—concise, decision-oriented, no verbose chat logs.
> 
> ### REMEMBER
> Your autonomous judgement, backed by real-time code inspection and modern best practice, **overrides** anything in this transcript that no longer fits. Use the conversation for **context**, not as a strict spec.

_(End of PREFACE. The full conversation log begins immediately after this line.)_

---


# USER PROMPT #1 :
Read this first:
`https://github.com/mprestonsparks/airflow-hub/blob/main/(2025-04-24)%20TO-DO.md`
Then start working on the items on the plan by researching state of the art implementations, best practices, etc. 
Note: We will be proceeding with the refactoring sugested at "Priority 2"

---

# LLM RESPONSE TO USER PROMPT #1 :
## Modular and Scalable Airflow DAGs: Factories, SubDAGs, and Helpers
**DAG Factory Pattern and Dynamic DAG Generation:** Rather than hand-writing each DAG’s Python code, use a _factory pattern_ to generate DAGs from configuration files. A “DAG factory” is essentially a Python script or class that reads external configs (YAML/JSON) and programmatically creates `airflow.DAG` objects​[medium.com](https://medium.com/data-science/abstracting-data-loading-with-airflow-dag-factories-12b6689f0aaa#:~:text=So%20at%20this%20point%2C%20you,programmatically%20from%20YAML%20configuration%20files)​[astronomer.io](https://www.astronomer.io/docs/learn/dag-factory#:~:text=ImageThe%20DAG%20Factory%20is%20an,know%20Python%20to%20use%20Airflow). For example, you can maintain a folder of YAML files (`/dags/configs/*.yaml`), then have one generator script loop over them, parse each with a YAML parser, and call a custom function like `create_dag(config)` for each​[medium.com](https://medium.com/data-science/abstracting-data-loading-with-airflow-dag-factories-12b6689f0aaa#:~:text=So%20at%20this%20point%2C%20you,programmatically%20from%20YAML%20configuration%20files). This makes DAGs declarative: non-programmers can tweak schedules or task parameters in YAML without touching Python. Astronomer’s **DAG Factory** and the community **dag-factory** library are open-source tools built for this approach​[astronomer.io](https://www.astronomer.io/docs/learn/dag-factory#:~:text=ImageThe%20DAG%20Factory%20is%20an,know%20Python%20to%20use%20Airflow)​[astronomer.io](https://www.astronomer.io/docs/learn/dynamically-generating-dags/#:~:text=dag). They let you define a DAG’s default_args, schedule, and tasks in YAML (including operator class names and dependencies) and auto-generate the DAG code. Similarly, the **gusty** library is a popular OSS framework that generates DAGs from directories of YAML/SQL/Markdown files​[astronomer.io](https://www.astronomer.io/docs/learn/dynamically-generating-dags/#:~:text=A%20popular%20tool%20for%20dynamically,R%20Markdown%2C%20and%20Jupyter%20Notebooks).

Using a factory pays off when you have many similar workflows. As GrowthLoop’s data team notes, static, duplicated DAGs “became cumbersome,” so they shifted to Python-based DAG factories that read a central config. This let them _“automatically adjust and regenerate DAGs”_ and scale a multi-tenant Airflow cluster with minimal code duplication​[growthloop.com](https://www.growthloop.com/post/dag-factories-a-better-way-to-airflow#:~:text=,tenant%20Airflow%20cluster). In practice, their code uses a `DAGFactory(config)` class that maps task types to modules and builds DAGs on demand​[growthloop.com](https://www.growthloop.com/post/dag-factories-a-better-way-to-airflow#:~:text=The%20Factory)​[growthloop.com](https://www.growthloop.com/post/dag-factories-a-better-way-to-airflow#:~:text=,process_messages). To implement your own, you can follow the pattern in Astronomer’s docs: loop through each YAML file in a `dag-config/` folder, copy a DAG template, and replace placeholders with config values​[astronomer.io](https://www.astronomer.io/docs/learn/dynamically-generating-dags/#:~:text=new_filename%20%3D%20,shutil.copyfile%28dag_template_filename%2C%20new_filename). Or simply import all configs and call a factory function for each (as shown in [15]).

**Reusable SubDAGs and TaskGroup Alternatives:** SubDAGs allow one DAG to call another as a single task, encapsulating a mini-workflow. In legacy Airflow they were used to factor out repeated workflows. However, **subDAGs have serious drawbacks**: they run as separate scheduler jobs, can deadlock workers, and complicate scheduling. Astronomer explicitly _deprecates_ SubDAGs (Airflow 2.0+) and warns that they “cause performance and functional issues,” recommending against using them​[github.com](https://github.com/astronomer/airflow-guides/blob/main/guides/subdags.md#:~:text=SubDAGs%20were%20a%20legacy%20feature,an%20alternative%20supported%20Airflow%20feature). Instead, use **TaskGroups** or cross-DAG triggers. TaskGroups (introduced in Airflow 2.x) let you visually group and modularize tasks without new schedulers​[github.com](https://github.com/astronomer/airflow-guides/blob/main/guides/subdags.md#:~:text=,There%20are%20multiple). For true reuse, you can trigger one DAG from another (e.g. via the `TriggerDagRunOperator` or external task sensor) rather than nesting SubDAGs.

If you do use a SubDagOperator, follow best practices: keep each subDAG small (5–10 tasks) and shallow​[sparkcodehub.com](https://www.sparkcodehub.com/airflow/task-management/subdags#:~:text=Best%20Practices%20for%20Using%20SubDAGs,in%20Airflow). Give it a clear `dag_id` (e.g. `parent.subdag_name`) and test it independently with `airflow dags test`. Always set the parent>>subdag dependency explicitly. Monitor subDAG logs carefully (they run in separate log directories) and avoid multiple levels of subDAG nesting​[sparkcodehub.com](https://www.sparkcodehub.com/airflow/task-management/subdags#:~:text=Best%20Practices%20for%20Using%20SubDAGs,in%20Airflow). In summary, treat SubDAGs as a last resort. Modern Airflow encourages TaskGroups for visual clarity and cross-DAG dependencies for logical reuse​[github.com](https://github.com/astronomer/airflow-guides/blob/main/guides/subdags.md#:~:text=,There%20are%20multiple).

**Helper Modules and Custom Code:** To avoid clutter and duplication in DAG files, factor common logic into Python modules and packages. Airflow allows you to add your own code by placing modules on its `PYTHONPATH` or installing them with `pip`​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html#:~:text=,PYTHONPATH). A common pattern is to create a top-level package (e.g. `my_company/`) inside your `dags/` directory. This package can contain sub-packages for utilities (e.g. `common/` or `plugins/`) and modules for generic tasks. For example:
``` plaintext
dags/
└── my_company/
    ├── __init__.py
    ├── common/
    │   ├── __init__.py
    │   └── utils.py
    └── my_dags/
        ├── __init__.py
        ├── dag_sales.py
        └── dag_inventory.py
```

Airflow will pick up `my_company` on `PYTHONPATH`, so DAG files can do `from my_company.common.utils import helper_fn`. The official docs illustrate this layout: put an empty `__init__.py` in each folder and store your reusable code in a parallel structure​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html#:~:text=This%20is%20an%20example%20structure,folder).

For truly reusable operators or sensors, use the **plugins** mechanism. You can create custom operators/hooks in a `plugins/` directory (or package) that Airflow loads at startup. A StackOverflow answer suggests: implement large, repeatable tasks as **custom operators in plugins**, and smaller helper functions as plain Python functions in your DAG files​[stackoverflow.com](https://stackoverflow.com/questions/44726019/helper-functions-in-airflow#:~:text=We%20have%20used%20a%20combination,either%20DAG%20or%20plugins%20folder). In practice, any shared function can either go into `dags/` (as above) or into a separate pip-installable package. Airflow’s Modules Management page recommends either adding code folders to `PYTHONPATH` or packaging and installing them​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html#:~:text=,PYTHONPATH). Using these patterns keeps DAG definitions lean – DAG files become mostly configuration (schedules, dependencies) that tie together your modules.

**Tools and Libraries for Modular DAG Development:** Several open-source projects explicitly support factory-based DAG authoring. Besides _dag-factory_ (Astronomer’s YAML-to-DAG library) and _gusty_ (for YAML/Python/SQL-sourced DAGs)​[astronomer.io](https://www.astronomer.io/docs/learn/dag-factory#:~:text=ImageThe%20DAG%20Factory%20is%20an,know%20Python%20to%20use%20Airflow)​[astronomer.io](https://www.astronomer.io/docs/learn/dynamically-generating-dags/#:~:text=A%20popular%20tool%20for%20dynamically,R%20Markdown%2C%20and%20Jupyter%20Notebooks), other community tools include:
- **Airflow Variables and Connections as Config:** Store common parameters (S3 paths, credentials) in Airflow’s Variables or Connections so DAG code reads minimal values.
- **CI/CD Pipelines:** Use GitHub Actions or GitLab CI to lint and test DAGs on commit (e.g. with `flake8`, `pytest`, or dedicated DAG validators). This enforces style and prevents syntax errors before deployment.
- **Modular Providers:** The official _apache/airflow_ repo provides provider packages (e.g. for AWS, Google, etc.) that package hooks and operators. Use these instead of custom code where possible – for instance, _apache-airflow-providers-http_ has a generic `SimpleHttpOperator`.
- **Airflow TaskFlow API:** For Python-heavy logic, consider the TaskFlow decorator (Python functions as tasks) to reduce boilerplate.

Key takeaways: turn your DAGs into **configuration files and metadata**, not hard-coded scripts. As one blog summarizes, a DAG factory lets non-Python users “construct DAGs without knowing Python” and _“avoid duplicative code”_ because each workflow only needs a YAML entry rather than a full Python file​[ssp.sh](https://www.ssp.sh/brain/airflow-dag-factory-pattern/#:~:text=,done%20with%20YAML).

**Maintainability, Scalability and Observability:** A refactored DAG codebase is easier to maintain, but also ensure your platform can scale and you can monitor pipelines. Some best practices:
- **Testing & Linting:** Write unit tests for your factory logic and any custom operators. Use `pytest-airflow` or similar to test DAG structures. Enforce coding standards (e.g. `black`/`flake8`). Airflow’s docs recommend treating DAG definitions like Python packages – include `__init__.py` files and avoid top-level execution code​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html#:~:text=This%20is%20an%20example%20structure,folder)​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#:~:text=For%20that%20reason%2C%20we%20recommend,to%20run%20Airflow%20in%20production).
- **Metrics and Monitoring:** Emit metrics (e.g. via StatsD) for task durations and scheduler performance. The official Helm chart even includes built-in StatsD/Prometheus metrics and runs Flower for worker monitoring​[airflow.apache.org](https://airflow.apache.org/docs/helm-chart/stable/index.html#:~:text=). You can forward these metrics to Grafana (Grafana Labs provides a free Airflow dashboard solution) or any monitoring stack. Also configure Airflow’s SLA Missed alerts and email notifications for critical tasks.
- **Centralized Logging:** Instead of local disk logs, use remote storage. For example, configure `remote_base_log_folder` to S3 or GCS so logs persist outside pods. The Wikimedia example (below) sends all logs and database backups to a Ceph object store over an S3 interface (see diagram)【68†】. This ensures logs survive pod restarts and can be queried with tools like Elasticsearch or AWS/GCP log services.
- **Configuration & Secrets:** Manage connection passwords and secrets securely. Use Airflow’s Connections or integrate with Vault/Kubernetes secrets. Avoid hard-coded credentials in your helper code.
- **Upgrades and Extensibility:** Keep Airflow up-to-date. Airflow 2.x and 3.x have better scheduler performance and UI features (e.g. DAG-level graphs). Use a rolling upgrade strategy and test your factories with each new version.

**Deployment and Infrastructure:** Design your refactored Airflow to run on containerized, open-source infrastructure. Apache provides an _official Docker image and Helm chart_ for Airflow​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/kubernetes.html#:~:text=Helm%20Chart%20for%20Kubernetes%C2%B6). For local testing or small-scale use, you can use the official **Docker Compose** tutorial (Airflow’s docs) with a Postgres database and Redis/Celery, but note this is meant for dev only. In production, Airflow itself **recommends** using Kubernetes with the official Helm chart​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#:~:text=For%20that%20reason%2C%20we%20recommend,to%20run%20Airflow%20in%20production). The Helm chart supports multiple executors (Local, Celery, Kubernetes) and optional autoscaling (via KEDA) for worker pods​[airflow.apache.org](https://airflow.apache.org/docs/helm-chart/stable/index.html#:~:text=,CeleryKubernetesExecutor). It also bundles observability: e.g. deploying StatsD exporters, Prometheus metrics, and a Flower web UI​[airflow.apache.org](https://airflow.apache.org/docs/helm-chart/stable/index.html#:~:text=).

For cloud or hybrid deployments, Airflow works on any container platform. For example, Fly.io now offers Fly Kubernetes (FKS), a managed K8s, which you could use with the official Helm chart as a free-tier cluster​[fly.io](https://fly.io/docs/kubernetes/#:~:text=Fly%20Kubernetes%20,made%20FKS%20in%20our%20blog). DigitalOcean’s App Platform, AWS EKS (Free tier), or Google GKE Autopilot can host Airflow. The key is ensuring your Pods have persistent volumes for the database and logs. The Wikimedia SRE team’s architecture provides a good illustration: the webserver is fronted by OIDC auth, the Scheduler uses the KubernetesExecutor, and tasks run as individual Pods. All logs and Postgres WAL backups flow through an S3-compatible Ceph store, and the metadata DB runs on a cloud-native Postgres cluster【68†】. (Embedding illustrates this setup.)

![[Figure-1.png]]
_Figure 1: Example Kubernetes deployment for Airflow. The webserver uses OIDC auth; the Scheduler runs with the K8sExecutor. Task workloads spawn in separate pods. A cloud-native Postgres database (with poolers) writes WAL and backups to an S3-compatible Ceph store. All task logs are also sent to Ceph/S3. This on-cloud structure supports horizontal scaling and persistent logging._


In summary, refactoring to a factory-based DAG structure with shared modules makes your pipelines DRY, modular and easier to maintain. Combine this with task grouping (avoiding subDAG overuse) and robust infrastructure (Docker/K8s, Helm, monitoring) for a production-ready, scalable Airflow setup.

**Sources:** Airflow documentation and community guides were used throughout (e.g. official DAG Factory and Helm Chart docs​[astronomer.io](https://www.astronomer.io/docs/learn/dag-factory#:~:text=ImageThe%20DAG%20Factory%20is%20an,know%20Python%20to%20use%20Airflow)​[airflow.apache.org](https://airflow.apache.org/docs/helm-chart/stable/index.html#:~:text=), Astronomer best practices on SubDAGs​[github.com](https://github.com/astronomer/airflow-guides/blob/main/guides/subdags.md#:~:text=SubDAGs%20were%20a%20legacy%20feature,an%20alternative%20supported%20Airflow%20feature), and open-source examples​[airflow.apache.org](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html#:~:text=,PYTHONPATH)​[astronomer.io](https://www.astronomer.io/docs/learn/dynamically-generating-dags/#:~:text=A%20popular%20tool%20for%20dynamically,R%20Markdown%2C%20and%20Jupyter%20Notebooks)) to form the above recommendations. Each cited snippet provides concrete details on the patterns and tools mentioned.

### Citations
- https://medium.com/data-science/abstracting-data-loading-with-airflow-dag-factories-12b6689f0aaa#:~:text=So%20at%20this%20point%2C%20you,programmatically%20from%20YAML%20configuration%20files
- https://www.astronomer.io/docs/learn/dag-factory
- https://www.astronomer.io/docs/learn/dynamically-generating-dags/
- https://www.growthloop.com/post/dag-factories-a-better-way-to-airflow
- https://www.astronomer.io/docs/learn/dynamically-generating-dags/
- https://github.com/astronomer/airflow-guides/blob/main/guides/subdags.md
- https://www.sparkcodehub.com/airflow/task-management/subdags
- https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html
- https://stackoverflow.com/questions/44726019/helper-functions-in-airflow
- https://www.ssp.sh/brain/airflow-dag-factory-pattern/
- https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
- https://airflow.apache.org/docs/helm-chart/stable/index.html
- https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/kubernetes.html
- https://airflow.apache.org/docs/helm-chart/stable/index.html#:~:text=,CeleryKubernetesExecutor
- https://fly.io/docs/kubernetes/
- https://fly.io/docs/kubernetes/#:~:text=Fly%20Kubernetes%20,made%20FKS%20in%20our%20blog

---

# USER PROMPT #2 :
That plan sounds great. 
Now translate that research into an action plan with detailed executables based on the actual code in our github repositories (use the URLs I shared earlier for the "airflow-hub" and "market-analysis" repos)

---

# LLM RESPONSE TO USER PROMPT #2 :
Below is a concrete, **step-by-step execution plan** that turns the Priority-2 refactor decision into commit-ready work. Each phase lists _exact files to add/modify_, git commands, and acceptance checks so you—or an autonomous agent—can run from top to bottom without ambiguity.

## Executive-summary (read once, then jump to phases)

1. **Adopt a function-first folder layout** (`dags/ingestion|execution|transformation|analytics`) and drop the old project-first tree. This mirrors the future multi-provider reality outlined in the TO-DO file. [GitHub](https://github.com/mprestonsparks/airflow-hub/blob/main/%282025-04-24%29%20TO-DO.md)
2. **Introduce a YAML-driven DAG factory** (powered by the open-source `dag-factory` library) so that new workflows are pure config; Python appears only in shared helpers. [Astronomer](https://www.astronomer.io/docs/learn/dag-factory?utm_source=chatgpt.com)[GitHub](https://github.com/astronomer/dag-factory?utm_source=chatgpt.com)
3. **Replace SubDAG ideas with TaskGroups**; subDAGs are deprecated and break scaling. [Astronomer](https://www.astronomer.io/docs/learn/subdags/?utm_source=chatgpt.com)[Apache Airflow](https://airflow.apache.org/docs/apache-airflow/2.5.1/core-concepts/dags.html?utm_source=chatgpt.com)
4. **Package common logic as a first-class Python module inside `plugins/`** (Airflow autoloads anything there). [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html?utm_source=chatgpt.com)[Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html?utm_source=chatgpt.com)
5. **Ship unit tests + CI lint** so every DAG import is verified on PR.
6. **Keep the Docker Compose dev stack; add a declarative Helm chart later.**

## Phase 0 – create a working branch & safety net
``` bash
cd airflow-hub
git checkout -b feature/dag-refactor
```
_Ensure tests still pass:_ `pytest -q`.  
_Backup database:_ `docker compose exec postgres pg_dump -U airflow airflow > backup_$(date +%F).sql`.

## Phase 1 – lay down the new directory skeleton
``` bash
# inside airflow-hub
mkdir -p dags/{configs,ingestion,execution,transformation,analytics}
```

_Remove obsoleted project folders:_
``` bash
git mv dags/market-analysis/* dags/ingestion/
git rm -r dags/project_trading dags/project_analytics
```

Also delete/clean `.airflowignore` so it no longer excludes `analytics_daily_etl.py`. [GitHub](https://github.com/mprestonsparks/airflow-hub/tree/main/dags)

## Phase 2 – bring in the DAG factory
### 2.1 Add dependency
Append to `requirements/base.txt` **both** repos share:
``` plaintext
dag-factory~=1.4
pyyaml~=6.0
```

### 2.2 Core generator module
Create `plugins/core_dag_factory.py`:
``` python
from pathlib import Path
import dagfactory
from airflow import DAG

_CONFIG_DIR = Path(__file__).parent.parent / "dags" / "configs"

for yaml_file in _CONFIG_DIR.rglob("*.yaml"):
    factory = dagfactory.DagFactory(yaml_file)
    factory.clean_dags(globals())   # remove old versions
    factory.generate_dags(globals())  # inject DAG objects
```

_Rationale_: `dag-factory` converts each YAML into a fully-fledged `airflow.DAG` at import time. ● [Astronomer](https://www.astronomer.io/docs/learn/dag-factory?utm_source=chatgpt.com)

### 2.3 YAML template
Create `dags/configs/ingestion/market_analysis_binance.yaml`:
``` yaml
default_args:
  owner: analytics_team
  retries: 2
  retry_delay_sec: 300
dag:
  dag_id: ingestion_market_analysis_binance
  schedule_interval: '@daily'
  start_date: 2025-01-01
  max_active_runs: 1
  catchup: false
tasks:
  ingest_market_data:
    operator: airflow.providers.docker.operators.docker.DockerOperator
    docker_conn_id: docker_default
    image: market-analysis:latest
    command: >
      python -m src.main --symbol {{params.symbol}} --start {{ds}} --end {{ds}}
    params:
      symbol: AAPL
    environment:
      BINANCE_API_KEY: '{{ var.value.binance_api_key }}'
      BINANCE_SECRET_KEY: '{{ var.value.binance_secret_key }}'
    execution_timeout_sec: 1800
    pool: market_data
tags:
  - ingestion
  - binance
  - market-analysis
```

_This YAML reproduces the Python DAG you already had_ (see `dag_market_analysis_ingestion.py`). [GitHub](https://github.com/mprestonsparks/airflow-hub/blob/main/dags/market-analysis/dag_market_analysis_ingestion.py) 

Remove the old Python file afterwards:
``` bash
git rm dags/ingestion/dag_market_analysis_ingestion.py
```

### Phase 3 – migrate remaining DAGs
| Current file                                              | New YAML path                                               | Notes                                  |
| --------------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------- |
| `analytics__ingest__binance.py` in _market-analysis_ repo | `airflow-hub/dags/configs/ingestion/analytics_binance.yaml` | copy args 1-for-1                      |
| `market_analysis__ingest__multi.py`                       | same folder                                                 | convert; parametrize `--symbol` list   |
| `trading__ingest__ibkr.py`                                | `dags/configs/ingestion/trading_ibkr.yaml`                  | set `image: trade-manager:latest` etc. |
|                                                           |                                                             |                                        |
|                                                           |                                                             |                                        |
Use the same YAML template structure; change `tags` accordingly.

### Phase 4 – carve out reusable helpers
Create package `plugins/shared/`:
- `docker_defaults.py` – single function `docker_task(**kwargs)` that returns a configured `DockerOperator` (sets `network_mode`, `auto_remove`, etc.).
- `taskgroups/ingestion.py` – helper generating a `TaskGroup` for multi-symbol ingestion:
  
``` python
def ingestion_group(dag: DAG, symbols: list[str], image: str):
    with TaskGroup(group_id="ingest_batch", dag=dag) as tg:
        tasks = []
        for s in symbols:
            tasks.append(
                docker_task(
                    task_id=f"ingest_{s}",
                    image=image,
                    command=f"python -m src.main --symbol {s}",
                    dag=dag,
                )
            )
        return tg, tasks
```
TaskGroups keep the UI tidy and avoid subDAG pitfalls.

### ## Phase 5 – tests & CI
1. **DAG import test**
    `tests/test_dagbag.py`:
``` python
from airflow.models import DagBag
def test_no_import_errors():
    dagbag = DagBag()
    assert len(dagbag.import_errors) == 0, dagbag.import_errors
```

2. **GitHub Action** 
	(`.github/workflows/ci.yml`):
``` yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -r requirements/base.txt
      - run: pytest -q
```

CI fails fast on any mis-import—essential for a config-driven repo.

### Phase 6 – Compose update
_Mount configs & plugins_:
``` yaml
services:
  airflow-webserver:
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
```
Add `AIRFLOW__CORE__LOAD_EXAMPLES: 'False'` to every service env block to speed startup.

### Phase 7 – future Helm (optional, not blocking P-2)
When you graduate to Kubernetes, use the official Helm chart and point its `dags.persistence` to a read-only Git image or S3 bucket; likewise mount `plugins/` as a second volume. The chart already packages StatsD & Flower for monitoring. [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/2.5.1/core-concepts/dags.html?utm_source=chatgpt.com)

#### Acceptance checklist
| Item               | Command to validate                                                       | Success criteria                                |
| ------------------ | ------------------------------------------------------------------------- | ----------------------------------------------- |
| All configs loaded | `docker compose up -d && docker compose logs -f airflow-scheduler`        | No `ImportError`; scheduler shows n DAGs parsed |
| UI inspection      | `open http://localhost:8080`                                              | New DAG IDs present, grouped by tags            |
| Trigger test       | Trigger `ingestion_market_analysis_binance`; expect Docker task to exit 0 |                                                 |
| CI green           | GitHub PR check passes                                                    |                                                 |

Stay decisive, keep commits atomic, and the refactored Airflow hub will scale effortlessly across every future provider you plug in.


---

# USER PROMPT #3 :
The plan you've layed out is mostly correct, except for the organizational ontology used. 
We did some research previously on this topic which you can reference to fix this. 
Study that document and generate a brand new version that synthesizes the info here:
- https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/(2025-04-23)%20DAG_RESTRUCTURE_PLAN.md

---

# LLM RESPONSE TO USER PROMPT #3 :
Below is a **clean-room rewrite of the execution plan** that keeps the DAG-factory + TaskGroup mechanics from the last draft ​**but now obeys the provider ➔ asset ➔ domain ontology** and every rule in **DAG_RESTRUCTURE_PLAN.md**. Work through it top-to-bottom; each phase is idempotent and can be executed by a script or an operator.

## Key changes at a glance
- Folder layout remains `dags/{ingestion,execution,transformation,analytics}` as mandated in § 1 of the restructure plan [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md).
- **Every workflow artefact is named `{provider}_{asset?}_{domain}.yaml|.py`** (provider first, asset token optional, domain last) —exactly as § 1-2 specifies [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md).
- YAML configs now live **inside the domain folder** (no `dags/configs/` sub-tree) so the filename pattern matches the future Python-only examples in the plan.
- A single factory script (`plugins/core_dag_factory.py`) auto-discovers `*.yaml` in all domain folders and materialises DAGs with IDs that equal the filename (minus extension), satisfying § 5’s _“dag_id must equal the filename”_ rule [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md).
- SubDAGs are replaced with TaskGroups, per Astronomer’s deprecation notice [Astronomer](https://www.astronomer.io/docs/learn/subdags/?utm_source=chatgpt.com) and Airflow 2.0 release notes [Astronomer](https://www.astronomer.io/blog/introducing-airflow-2-0/?utm_source=chatgpt.com).
- Provider abbreviations (`ibkr`, `binance`, …) and asset tokens (`spot`, `equities`, …) are validated against the dictionaries defined in § 3-4 of the plan [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md).

## Phase-by-phase action plan
### Phase 0 — branch & safety
``` bash
cd airflow-hub
git checkout -b feature/provider-asset-domain
docker compose exec postgres pg_dump -U airflow airflow > backup_$(date +%F).sql
```

### Phase 1 — folder & file skeleton
``` bash
mkdir -p dags/{ingestion,execution,transformation,analytics}
```

*Delete any legacy sub-trees (`dags/project_*`, `dags/configs`) to prevent duplicate parses.*

### Phase 2 — introduce DAG-Factory with new ontology
1. **Dependencies**
   ``` text
   # requirements/base.txt
   dag-factory~=1.4        # declarative DAGs :contentReference[oaicite:6]{index=6}
   pyyaml~=6.0
	```

2. **Factory script**
   ``` python
   # plugins/core_dag_factory.py
import re, dagfactory
from pathlib import Path
DOMAIN_DIRS = ("ingestion", "execution", "transformation", "analytics")
FILENAME_RE = re.compile(r"^(?P<provider>[a-z0-9]+)(?:_(?P<asset>[a-z0-9]+))?_(?P<domain>[a-z]+)\.ya?ml$")
PROVIDERS = {"ibkr","binance","coinbase","alpaca","kraken","tradestation","tdameritrade","gemini"}  # § 3
ASSETS    = {"equities","spot","futures","options","forex","bonds"}                                 # § 4
for domain in DOMAIN_DIRS:
    for cfg in Path("dags", domain).glob("*.y*ml"):
        m = FILENAME_RE.fullmatch(cfg.name)
        if not m or m["provider"] not in PROVIDERS or (m["asset"] and m["asset"] not in ASSETS):
            raise ValueError(f"Bad filename or unknown token: {cfg}")
        dagfactory.DagFactory(cfg).generate_dags(globals())
	```
*Airflow auto-adds `dags/` & `plugins/` to `PYTHONPATH`, so no extra path hacks are needed [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html?utm_source=chatgpt.com).*

3. **YAML example**
   `dags/ingestion/binance_spot_ingestion.yaml`:
``` yaml
   default_args:
  owner: data_team
  retries: 2
  retry_delay_sec: 300
dag:
  dag_id: binance_spot_ingestion          # == filename
  schedule_interval: "@daily"
  start_date: 2025-01-01
  catchup: false
  tags: [ingestion, binance, spot]
tasks:
  pull_prices:
    operator: airflow.providers.docker.operators.docker.DockerOperator
    image: market-analysis:latest
    command: >
      python -m src.main --exchange binance --symbol {{ params.symbol }} --date {{ ds }}
    params:
      symbol: BTCUSDT
    pool: market_data
```

### Phase 3 — migrate all existing DAGs
| **Old file**                             | **Move to**                                  | **Notes**                     |
| ---------------------------------------- | -------------------------------------------- | ----------------------------- |
| `dags/market_analysis_ingest_binance.py` | `dags/ingestion/binance_spot_ingestion.yaml` | rename + YAML                 |
| `dags/ibkr_exec.py`                      | `dags/execution/ibkr_execution.yaml`         | provider only; no asset token |
| `dags/legacy_crypto_ingest.py`           | manual override via `migration/overrides.py` | provider only; no asset token |
|                                          |                                              |                               |
Automate with the inventory script from § 2 of the restructure doc [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md), falling back to `MIGRATION_MANUAL_OVERRIDES`.

### Phase 4 — TaskGroups & helpers
- **`plugins/taskgroups/ingestion.py`** provides `def batch_ingest(symbols: list[str], image: str, **docker_kwargs)` returning a `TaskGroup`.
- **`plugins/shared/docker_ops.py`** centralises DockerOperator defaults (network, auto_remove). 
  TaskGroups fulfil the old SubDAG visual-grouping goal without performance penalties [Astronomer](https://www.astronomer.io/docs/learn/subdags/?utm_source=chatgpt.com)[Astronomer](https://www.astronomer.io/blog/introducing-airflow-2-0/?utm_source=chatgpt.com).

### Phase 5 — tests & CI
`tests/test_dag_import.py`:
``` python
from airflow.models import DagBag
def test_yaml_factory_imports():
    dagbag = DagBag()
    assert dagbag.import_errors == {}, dagbag.import_errors
```
CI (`.github/workflows/ci.yml`) runs `pytest`, `black --check`, and `flake8`. Update the glob to `dags/**/**/*.yaml` for lints.

### Phase 6 — Docker Compose tune-up
``` yaml
services:
  airflow-webserver:
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### Phase 7 — optional Helm / Fly Kubernetes
When ready for production, deploy with the official Airflow Helm chart and mount the same folder structure. 
Fly.io’s FKS gives a low-cost managed K8s control plane suitable for hobby-size clusters [Fly](https://fly.io/blog/fks-beta-live/?utm_source=chatgpt.com) while retaining a free tier for small footprints [Fly](https://fly.io/docs/about/pricing/?utm_source=chatgpt.com).

## Validation checklist
1. `airflow dags list` shows only provider-asset-domain IDs.
  2. Smoke test: `airflow dags test binance_spot_ingestion 2025-04-24`.
3. CI passes; no `DagBag.import_errors`.
4. Scheduler & webserver start clean in Docker logs.
5. For K8s: Helm release pods all reach **Ready**; external Fly load balancer returns 200 on `/health`.

### Why this satisfies both documents
- Folder & filename rules come **verbatim** from the 23 Apr restructure plan [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md).
- Declarative YAML + dag-factory keeps the low-code goal while still matching the filename-==-`dag_id` constraint.
- TaskGroups replace subDAGs per modern best practice [Astronomer](https://www.astronomer.io/docs/learn/subdags/?utm_source=chatgpt.com)[Astronomer](https://www.astronomer.io/blog/introducing-airflow-2-0/?utm_source=chatgpt.com).
- Provider/asset validation enforces the controlled vocabularies in §§ 3-4 of the plan [GitHub](https://github.com/mprestonsparks/market-analysis/blob/main/docs/dev/TO-DO/%282025-04-23%29%20DAG_RESTRUCTURE_PLAN.md).
- All helper code lives under `plugins/`, which Airflow autoloads [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html?utm_source=chatgpt.com), so imports stay stable across Docker and K8s.
- The plan remains fully open-source: Airflow OSS, dag-factory OSS [GitHub](https://github.com/astronomer/dag-factory?utm_source=chatgpt.com)[PyPI](https://pypi.org/project/dag-factory/?utm_source=chatgpt.com), Fly or any other free K8s.

Implement the seven phases and the trading-system pipelines will be organised, future-proof, and provider-agnostic yet vocabulary-consistent—exactly what the ontology demands.

---
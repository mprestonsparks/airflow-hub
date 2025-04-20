# Integration Quickstart

This quickstart guide walks you through getting the Docker‑based Airflow monorepo up and running.

## Prerequisites
- Docker & Docker Compose installed on your machine
- (Optional) Local Python 3.8+ for CLI development

## 1. Clone the Repository
```bash
git clone https://github.com/mprestonsparks/airflow-hub.git
cd airflow-hub
```

## 2. Build Docker Images
```bash
docker-compose build
```

## 3. Initialize the Airflow Database
```bash
docker-compose run --rm airflow-init
```

## 4. Start Airflow Services
```bash
docker-compose up -d
```

## 5. Verify DAGs
```bash
docker-compose exec airflow-webserver airflow dags list
docker-compose exec airflow-webserver airflow dags list-import-errors
```

## 6. Run Tests
```bash
pytest tests/test_dag_validation.py
```

## 7. Access the Airflow UI
Open your browser at http://localhost:8080
- Username: airflow
- Password: airflow

## Next Steps
- Author new DAGs under `dags/<project_name>/`
- Place reusable code in `plugins/common/`
- Use `DockerOperator` for project-specific containers
- See `docs/integration_guide.md` for full integration patterns
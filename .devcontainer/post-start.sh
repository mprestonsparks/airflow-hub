#!/bin/bash

# Airflow Hub Post-Start Script
# This script runs every time the container starts

set -e

echo "🔄 Starting Airflow Hub services..."

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Set up Airflow environment variables
export AIRFLOW_HOME=/workspaces/airflow-hub
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@host.docker.internal:5432/airflow
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=true

# =============================================================================
# DATABASE CONNECTION CHECK
# =============================================================================

echo "🗄️ Checking database connectivity..."

# Wait for PostgreSQL to be available
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h host.docker.internal -p 5432 -U airflow; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✅ PostgreSQL is ready"

# =============================================================================
# AIRFLOW DATABASE INITIALIZATION
# =============================================================================

echo "🔧 Checking Airflow database..."

# Check if Airflow database is initialized
if ! airflow db check >/dev/null 2>&1; then
    echo "📝 Initializing Airflow database..."
    airflow db init
    
    # Create admin user if it doesn't exist
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin || echo "Admin user already exists"
    
    echo "✅ Airflow database initialized"
else
    echo "✅ Airflow database is ready"
fi

# =============================================================================
# DAG VALIDATION
# =============================================================================

echo "📋 Validating DAGs..."

# Check DAG syntax
if [ -d "dags" ] && [ "$(ls -A dags/)" ]; then
    echo "🔍 Checking DAG syntax..."
    for dag_file in dags/*.py; do
        if [ -f "$dag_file" ]; then
            python -m py_compile "$dag_file" && echo "✅ $dag_file syntax OK" || echo "❌ $dag_file has syntax errors"
        fi
    done
    
    # List available DAGs
    echo "📋 Available DAGs:"
    airflow dags list 2>/dev/null || echo "No DAGs found or Airflow not ready"
else
    echo "⚠️  No DAGs found in dags/ directory"
fi

# =============================================================================
# VAULT INTEGRATION CHECK
# =============================================================================

echo "🔐 Checking Vault connectivity..."

export VAULT_ADDR=http://host.docker.internal:8200

# Check if Vault is available
if curl -s $VAULT_ADDR/v1/sys/health >/dev/null 2>&1; then
    echo "✅ Vault is accessible"
    
    # Test Vault authentication if token is available
    if [ -n "$VAULT_TOKEN" ]; then
        vault auth -method=token >/dev/null 2>&1 && echo "✅ Vault authentication successful" || echo "⚠️  Vault authentication failed"
    fi
else
    echo "⚠️  Vault is not accessible"
fi

# =============================================================================
# AIRFLOW SERVICES MANAGEMENT
# =============================================================================

echo "🚀 Managing Airflow services..."

# Function to check if a process is running
is_running() {
    pgrep -f "$1" >/dev/null
}

# Check and start Airflow scheduler
if ! is_running "airflow scheduler"; then
    echo "🔄 Starting Airflow scheduler..."
    nohup airflow scheduler > /logs/airflow-scheduler.log 2>&1 &
    sleep 3
    if is_running "airflow scheduler"; then
        echo "✅ Airflow scheduler started"
    else
        echo "❌ Failed to start Airflow scheduler"
    fi
else
    echo "✅ Airflow scheduler is already running"
fi

# Check and start Airflow webserver
if ! is_running "airflow webserver"; then
    echo "🌐 Starting Airflow webserver..."
    nohup airflow webserver --port 8080 > /logs/airflow-webserver.log 2>&1 &
    sleep 5
    if is_running "airflow webserver"; then
        echo "✅ Airflow webserver started on port 8080"
    else
        echo "❌ Failed to start Airflow webserver"
    fi
else
    echo "✅ Airflow webserver is already running"
fi

# =============================================================================
# HEALTH CHECKS
# =============================================================================

echo "🏥 Performing health checks..."

# Wait for webserver to be ready
echo "⏳ Waiting for Airflow webserver to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health >/dev/null 2>&1; then
        echo "✅ Airflow webserver is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Airflow webserver health check timeout"
    fi
    sleep 2
done

# Check scheduler health
if is_running "airflow scheduler"; then
    echo "✅ Airflow scheduler is running"
else
    echo "❌ Airflow scheduler is not running"
fi

# =============================================================================
# DEVELOPMENT ENVIRONMENT STATUS
# =============================================================================

echo ""
echo "📊 Airflow Hub Status Summary:"
echo "================================"

# Service status
echo "🔧 Services:"
echo "   - PostgreSQL: $(pg_isready -h host.docker.internal -p 5432 -U airflow >/dev/null 2>&1 && echo "✅ Connected" || echo "❌ Disconnected")"
echo "   - Vault: $(curl -s http://host.docker.internal:8200/v1/sys/health >/dev/null 2>&1 && echo "✅ Connected" || echo "❌ Disconnected")"
echo "   - Airflow Scheduler: $(is_running "airflow scheduler" && echo "✅ Running" || echo "❌ Stopped")"
echo "   - Airflow Webserver: $(is_running "airflow webserver" && echo "✅ Running" || echo "❌ Stopped")"

# DAG status
echo ""
echo "📋 DAGs:"
dag_count=$(airflow dags list 2>/dev/null | wc -l || echo "0")
echo "   - Total DAGs: $dag_count"

# Access information
echo ""
echo "🌐 Access Information:"
echo "   - Airflow UI: http://localhost:8080"
echo "   - Username: admin"
echo "   - Password: admin"

# Log locations
echo ""
echo "📝 Log Locations:"
echo "   - Scheduler: /logs/airflow-scheduler.log"
echo "   - Webserver: /logs/airflow-webserver.log"
echo "   - DAG Logs: $AIRFLOW_HOME/logs/"

echo ""
echo "💡 Quick commands:"
echo "   - 'make help' - Show available commands"
echo "   - 'airflow dags list' - List all DAGs"
echo "   - 'airflow dags trigger sample_dag' - Trigger sample DAG"
echo "   - 'make test' - Run tests"
echo "   - 'make check-dags' - Validate DAG syntax"

echo ""
echo "🎉 Airflow Hub is ready for development!"
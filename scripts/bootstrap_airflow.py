"""
Script to provision Airflow connections and pools for all integrated projects.

This script is meant to be run inside the Airflow environment (e.g., via docker exec or as an Airflow CLI task).
It ensures all required connections and pools are present, using environment variables or secrets for credentials.

Rationale: This automates setup, avoids manual errors, and supports reproducible, secure onboarding for new environments.
"""
import os
from airflow.models import Connection, Pool
from airflow import settings
from airflow.utils.db import provide_session

def get_env_or_default(var, default=None):
    return os.environ.get(var, default)

@provide_session
def upsert_connection(conn_id, conn_type, host=None, login=None, password=None, extra=None, session=None):
    conn = session.query(Connection).filter(Connection.conn_id == conn_id).one_or_none()
    if conn is None:
        conn = Connection(conn_id=conn_id, conn_type=conn_type, host=host, login=login, password=password, extra=extra)
        session.add(conn)
        print(f"[INFO] Created connection: {conn_id}")
    else:
        conn.conn_type = conn_type
        conn.host = host
        conn.login = login
        conn.password = password
        conn.extra = extra
        print(f"[INFO] Updated connection: {conn_id}")
    session.commit()

@provide_session
def upsert_pool(pool_name, slots, description, session=None):
    pool = session.query(Pool).filter(Pool.pool == pool_name).one_or_none()
    if pool is None:
        pool = Pool(pool=pool_name, slots=slots, description=description)
        session.add(pool)
        print(f"[INFO] Created pool: {pool_name}")
    else:
        pool.slots = slots
        pool.description = description
        print(f"[INFO] Updated pool: {pool_name}")
    session.commit()

if __name__ == "__main__":
    # Example: Market Analysis IBKR Connection
    upsert_connection(
        conn_id="market_analysis_ibkr",
        conn_type="http",
        host=get_env_or_default("IBKR_HOST", "localhost"),
        login=get_env_or_default("IBKR_CLIENT_ID", "default_id"),
        password=get_env_or_default("IBKR_PASSWORD", None),
        extra=None,
    )
    # Example: Market Analysis Binance Connection
    upsert_connection(
        conn_id="market_analysis_binance",
        conn_type="http",
        host="https://api.binance.com",
        login=get_env_or_default("BINANCE_API_KEY", None),
        password=get_env_or_default("BINANCE_API_SECRET", None),
        extra=None,
    )
    # Project Trading Pool
    upsert_pool(
        pool_name="project_trading_pool",
        slots=5,
        description="Dedicated pool for project_trading tasks."
    )
    # Add more connections/pools as new projects integrate
    print("[INFO] Airflow bootstrap complete.")

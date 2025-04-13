"""
Daily analytics ETL DAG.

This DAG extracts data from various sources, performs transformations and data quality checks,
and loads the processed data into analytics tables for reporting and ML models.
"""

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.python import PythonOperator
from plugins.project_analytics.operators import DataQualityOperator, MLPredictionOperator

# Configuration with project-specific naming conventions
DEFAULT_ARGS = {
    'owner': 'analytics_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': 300,  # 5 minutes
    'pool': 'project_analytics_pool',  # Project-specific resource pool
}

# DAG ID has project prefix for clear identification
dag = DAG(
    'project_analytics_daily_etl',
    default_args=DEFAULT_ARGS,
    description='Daily ETL process for analytics data',
    schedule_interval='0 2 * * *',  # 2:00 AM daily
    start_date=days_ago(1),
    tags=['analytics', 'etl', 'ml'],
)

# Extract and transform data from source systems
extract_transform_task = SnowflakeOperator(
    task_id='extract_transform_data',
    snowflake_conn_id='project_analytics_snowflake',
    sql='''
    -- Extract and transform data for analytics
    CALL analytics.etl_process_daily('{{ ds }}');
    ''',
    dag=dag,
)

# Run data quality checks on processed data
data_quality_task = DataQualityOperator(
    task_id='check_data_quality',
    conn_id='project_analytics_snowflake',
    table='analytics.processed_data',
    checks=[
        {'type': 'not_null', 'columns': ['customer_id', 'transaction_date', 'amount']},
        {'type': 'unique', 'columns': ['transaction_id']},
        {'type': 'value_range', 'column': 'amount', 'min': 0},
        {'type': 'row_count', 'min_rows': 1}
    ],
    fail_on_error=True,
    dag=dag,
)

# Run ML predictions on processed data
ml_prediction_task = MLPredictionOperator(
    task_id='run_ml_predictions',
    conn_id='project_analytics_snowflake',
    model_path='/opt/airflow/ml_models/customer_churn_model.pkl',
    input_query='''
    SELECT 
        customer_id,
        avg_transaction_value,
        transaction_frequency,
        days_since_last_purchase,
        total_purchases,
        product_categories_count
    FROM analytics.customer_features
    WHERE data_date = '{{ ds }}'
    ''',
    output_table='analytics.churn_predictions',
    features=[
        'avg_transaction_value',
        'transaction_frequency',
        'days_since_last_purchase',
        'total_purchases',
        'product_categories_count'
    ],
    id_column='customer_id',
    dag=dag,
)

# Generate analytics reports
generate_reports_task = SnowflakeOperator(
    task_id='generate_reports',
    snowflake_conn_id='project_analytics_snowflake',
    sql='''
    -- Generate daily analytics reports
    CALL analytics.generate_daily_reports('{{ ds }}');
    ''',
    dag=dag,
)

# Define task dependencies
extract_transform_task >> data_quality_task >> ml_prediction_task >> generate_reports_task

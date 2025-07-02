from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.email.operators.email import EmailOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import subprocess
import json
import os
import logging

logger = logging.getLogger(__name__)

def run_tests(**context):
    """Execute test suite and capture results."""
    # Get configuration from Airflow Variables
    test_command = Variable.get("test_command", "pytest")
    test_args = Variable.get("test_args", "--cov=. --cov-report=json --cov-report=html --json-report --json-report-file=test_results.json")
    repo_path = Variable.get("repo_path", "/opt/airflow/dags/repo")
    
    # Change to repository directory
    os.chdir(repo_path)
    
    # Run tests
    cmd = f"{test_command} {test_args}"
    logger.info(f"Running tests: {cmd}")
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit code
        )
        
        # Log output
        logger.info(f"Test stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Test stderr: {result.stderr}")
        
        # Parse test results
        test_results = {
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
        
        # Try to parse JSON report if it exists
        if os.path.exists("test_results.json"):
            with open("test_results.json", "r") as f:
                test_results["detailed_results"] = json.load(f)
        
        # Push results to XCom for next tasks
        context['ti'].xcom_push(key='test_results', value=test_results)
        
        # Fail task if tests failed (optional - can be configured)
        if result.returncode != 0:
            logger.warning(f"Tests failed with exit code {result.returncode}")
            # Optionally raise to fail the task
            # raise Exception(f"Tests failed with exit code {result.returncode}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Failed to run tests: {e}")
        raise

def generate_coverage_report(**context):
    """Generate and publish coverage report."""
    # Get test results from previous task
    test_results = context['ti'].xcom_pull(task_ids='run_tests', key='test_results')
    
    # Get configuration
    repo_path = Variable.get("repo_path", "/opt/airflow/dags/repo")
    coverage_threshold = float(Variable.get("coverage_threshold", "80"))
    report_storage_path = Variable.get("coverage_report_path", "/opt/airflow/reports/coverage")
    
    os.chdir(repo_path)
    
    coverage_data = {}
    
    try:
        # Read coverage JSON if it exists
        if os.path.exists("coverage.json"):
            with open("coverage.json", "r") as f:
                coverage_json = json.load(f)
                
            # Extract coverage percentage
            total_coverage = coverage_json.get("totals", {}).get("percent_covered", 0)
            coverage_data["total_coverage"] = total_coverage
            coverage_data["meets_threshold"] = total_coverage >= coverage_threshold
            
            # Get file-level coverage
            files_coverage = []
            for file_path, file_data in coverage_json.get("files", {}).items():
                files_coverage.append({
                    "file": file_path,
                    "coverage": file_data.get("summary", {}).get("percent_covered", 0),
                    "missing_lines": file_data.get("missing_lines", [])
                })
            
            # Sort by lowest coverage first
            files_coverage.sort(key=lambda x: x["coverage"])
            coverage_data["files"] = files_coverage[:10]  # Top 10 files with lowest coverage
            
        # Generate HTML report if not exists
        if not os.path.exists("htmlcov/index.html"):
            subprocess.run(["coverage", "html"], check=True)
        
        # Copy HTML report to storage location
        os.makedirs(report_storage_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dest = os.path.join(report_storage_path, f"coverage_{timestamp}")
        
        if os.path.exists("htmlcov"):
            subprocess.run(["cp", "-r", "htmlcov", report_dest], check=True)
            coverage_data["report_location"] = report_dest
            logger.info(f"Coverage report saved to {report_dest}")
        
        # Store coverage data in database (if configured)
        if Variable.get("store_coverage_metrics", "false").lower() == "true":
            # This would store in your metrics database
            # For now, just log it
            logger.info(f"Coverage metrics: {json.dumps(coverage_data, indent=2)}")
        
        # Push coverage data to XCom
        context['ti'].xcom_push(key='coverage_data', value=coverage_data)
        
        return coverage_data
        
    except Exception as e:
        logger.error(f"Failed to generate coverage report: {e}")
        raise

def notify_stakeholders(**context):
    """Send notifications about test results and coverage."""
    # Get results from previous tasks
    test_results = context['ti'].xcom_pull(task_ids='run_tests', key='test_results')
    coverage_data = context['ti'].xcom_pull(task_ids='generate_coverage_report', key='coverage_data')
    
    # Get notification configuration
    notification_method = Variable.get("notification_method", "log")  # log, email, slack, webhook
    
    # Build notification message
    tests_passed = test_results.get("passed", False)
    total_coverage = coverage_data.get("total_coverage", 0)
    meets_threshold = coverage_data.get("meets_threshold", False)
    
    status_emoji = "✅" if tests_passed and meets_threshold else "❌"
    
    message = f"""
{status_emoji} Test Results Summary

Repository: {Variable.get("repo_name", "Unknown")}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Test Results:
- Status: {"PASSED" if tests_passed else "FAILED"}
- Exit Code: {test_results.get("exit_code", "Unknown")}

Coverage Results:
- Total Coverage: {total_coverage:.1f}%
- Threshold: {Variable.get("coverage_threshold", "80")}%
- Meets Threshold: {"YES" if meets_threshold else "NO"}

Files with Lowest Coverage:
"""
    
    # Add files with lowest coverage
    for file_info in coverage_data.get("files", [])[:5]:
        message += f"- {file_info['file']}: {file_info['coverage']:.1f}%\n"
    
    if coverage_data.get("report_location"):
        message += f"\nFull report available at: {coverage_data['report_location']}"
    
    # Send notification based on method
    if notification_method == "email":
        email_to = Variable.get("notification_emails", "").split(",")
        if email_to:
            # This would use EmailOperator in the DAG definition
            logger.info(f"Would send email to: {email_to}")
            logger.info(f"Email content: {message}")
    
    elif notification_method == "slack":
        webhook_url = Variable.get("slack_webhook_url", "")
        if webhook_url:
            # Send to Slack
            import requests
            payload = {
                "text": message,
                "username": "Test Bot",
                "icon_emoji": ":test_tube:"
            }
            try:
                response = requests.post(webhook_url, json=payload)
                response.raise_for_status()
                logger.info("Notification sent to Slack")
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")
    
    elif notification_method == "webhook":
        webhook_url = Variable.get("notification_webhook_url", "")
        if webhook_url:
            # Send to generic webhook
            import requests
            payload = {
                "message": message,
                "test_results": test_results,
                "coverage_data": coverage_data,
                "timestamp": datetime.now().isoformat()
            }
            try:
                response = requests.post(webhook_url, json=payload)
                response.raise_for_status()
                logger.info("Notification sent to webhook")
            except Exception as e:
                logger.error(f"Failed to send webhook notification: {e}")
    
    else:
        # Default: just log
        logger.info(f"Test notification:\n{message}")
    
    return {
        "notification_sent": True,
        "method": notification_method,
        "message": message
    }

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'nightly_test_improve',
    default_args=default_args,
    description='A DAG to enhance test coverage and automate testing processes',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 5, 2),
    catchup=False,
) as dag:

    run_tests_task = PythonOperator(
        task_id='run_tests',
        python_callable=run_tests,
    )

    generate_coverage_report_task = PythonOperator(
        task_id='generate_coverage_report',
        python_callable=generate_coverage_report,
    )

    notify_stakeholders_task = PythonOperator(
        task_id='notify_stakeholders',
        python_callable=notify_stakeholders,
    )

    run_tests_task >> generate_coverage_report_task >> notify_stakeholders_task
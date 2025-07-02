"""
DEAN System Maintenance DAG

Handles system maintenance tasks including cleanup, monitoring, 
performance optimization, and system health checks.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup

# Import DEAN hooks
import sys
sys.path.insert(0, '/opt/airflow')
from plugins.agent_evolution.hooks.dean_api_hook import DeanApiHook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    'owner': 'dean-system',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'execution_timeout': timedelta(minutes=20),
}


def check_resource_usage(**context) -> Dict[str, Any]:
    """Check current system resource usage."""
    try:
        # In real implementation, would check actual system resources
        # Simulate resource monitoring
        resource_usage = {
            "cpu_usage": 0.65,
            "memory_usage": 0.75,
            "disk_usage": 0.82,  # Above threshold
            "worktree_count": 23,  # Above threshold
            "active_agents": 12,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get maintenance parameters
        params = context.get('params', {})
        resource_threshold = params.get('resource_threshold', 0.8)
        
        # Determine if cleanup is needed
        cleanup_needed = (
            resource_usage["disk_usage"] > resource_threshold or
            resource_usage["worktree_count"] > 20 or
            resource_usage["memory_usage"] > resource_threshold
        )
        
        result = {
            "resource_usage": resource_usage,
            "cleanup_needed": cleanup_needed,
            "resource_threshold": resource_threshold,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Resource usage check completed: {result}")
        return result
        
    except Exception as e:
        error_context = ErrorContext(
            error_type="ResourceCheckError",
            error_message=str(e),
            task_id="check_resource_usage",
            remediation_steps=[
                "Check system monitoring tools",
                "Verify resource collection scripts",
                "Review threshold configurations"
            ]
        )
        logger.error(f"Resource usage check failed: {error_context.to_dict()}")
        raise


def cleanup_worktrees(**context) -> Dict[str, Any]:
    """Clean up old git worktrees to free disk space."""
    try:
        ti = context['ti']
        resource_data = ti.xcom_pull(task_ids='check_resource_usage')
        
        cleanup_needed = resource_data['cleanup_needed']
        
        if not cleanup_needed:
            logger.info("No cleanup needed - resource usage within limits")
            return {
                "worktrees_cleaned": 0,
                "space_freed_gb": 0.0,
                "cleanup_reason": "not_needed",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get maintenance parameters
        params = context.get('params', {})
        cleanup_age_hours = params.get('cleanup_age_hours', 24)
        
        # Simulate worktree cleanup
        # In real implementation, would:
        # 1. Find worktrees older than cleanup_age_hours
        # 2. Verify they're not in use
        # 3. Remove them and calculate space freed
        
        mock_cleanup_results = {
            "worktrees_cleaned": 8,
            "space_freed_gb": 2.5,
            "cleanup_age_hours": cleanup_age_hours,
            "cleanup_reason": "resource_threshold_exceeded",
            "cleaned_worktrees": [
                f"worktree-{i}-{datetime.now().strftime('%Y%m%d')}" 
                for i in range(1, 9)
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Worktree cleanup completed: {mock_cleanup_results}")
        return mock_cleanup_results
        
    except Exception as e:
        error_context = ErrorContext(
            error_type="WorktreeCleanupError",
            error_message=str(e),
            task_id="cleanup_worktrees",
            remediation_steps=[
                "Check git worktree management scripts",
                "Verify worktree age detection logic",
                "Review cleanup permissions and access"
            ]
        )
        logger.error(f"Worktree cleanup failed: {error_context.to_dict()}")
        raise


def archive_agents(**context) -> Dict[str, Any]:
    """Archive inactive or old agents to free resources."""
    try:
        ti = context['ti']
        resource_data = ti.xcom_pull(task_ids='check_resource_usage')
        
        # Get maintenance parameters
        params = context.get('params', {})
        archive_enabled = params.get('archive_agents', True)
        
        if not archive_enabled:
            logger.info("Agent archiving disabled")
            return {
                "agents_archived": [],
                "archive_reason": "disabled",
                "timestamp": datetime.now().isoformat()
            }
        
        # Simulate agent archival
        # In real implementation, would:
        # 1. Identify inactive agents (no activity for X days)
        # 2. Archive their data to long-term storage
        # 3. Remove from active system
        
        current_agents = resource_data['resource_usage']['active_agents']
        
        # Archive agents if we have too many
        archived_agents = []
        if current_agents > 15:  # Max active agents threshold
            agents_to_archive = min(3, current_agents - 15)
            archived_agents = [
                f"archived-agent-{i}-{datetime.now().strftime('%Y%m%d')}"
                for i in range(agents_to_archive)
            ]
        
        result = {
            "agents_archived": archived_agents,
            "archive_reason": "resource_optimization" if archived_agents else "not_needed",
            "agents_before": current_agents,
            "agents_after": current_agents - len(archived_agents),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Agent archival completed: {result}")
        return result
        
    except Exception as e:
        error_context = ErrorContext(
            error_type="AgentArchivalError",
            error_message=str(e),
            task_id="archive_agents",
            remediation_steps=[
                "Check agent activity tracking",
                "Verify archival storage availability",
                "Review agent lifecycle management"
            ]
        )
        logger.error(f"Agent archival failed: {error_context.to_dict()}")
        raise


def rebalance_allocation(**context) -> Dict[str, Any]:
    """Rebalance resource allocation across remaining agents."""
    try:
        ti = context['ti']
        cleanup_data = ti.xcom_pull(task_ids='cleanup_worktrees')
        archive_data = ti.xcom_pull(task_ids='archive_agents')
        
        # Calculate available resources after cleanup
        space_freed = cleanup_data.get('space_freed_gb', 0.0)
        agents_archived = len(archive_data.get('agents_archived', []))
        
        rebalancing_actions = []
        
        if space_freed > 0:
            rebalancing_actions.append(f"Redistributed {space_freed:.1f}GB freed disk space")
            
        if agents_archived > 0:
            rebalancing_actions.append(f"Reallocated resources from {agents_archived} archived agents")
            
        # Simulate resource reallocation
        agents_rebalanced = 0
        if space_freed > 1.0 or agents_archived > 0:
            # Would rebalance token budgets, memory allocation, etc.
            agents_rebalanced = 12  # Mock rebalanced count
            rebalancing_actions.append(f"Rebalanced allocation for {agents_rebalanced} active agents")
        
        result = {
            "agents_rebalanced": agents_rebalanced,
            "rebalancing_actions": rebalancing_actions,
            "space_freed_gb": space_freed,
            "agents_archived": agents_archived,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Resource rebalancing completed: {result}")
        return result
        
    except Exception as e:
        error_context = ErrorContext(
            error_type="RebalancingError",
            error_message=str(e),
            task_id="rebalance_allocation",
            remediation_steps=[
                "Check resource allocation algorithms",
                "Verify agent resource tracking",
                "Review rebalancing logic"
            ]
        )
        logger.error(f"Resource rebalancing failed: {error_context.to_dict()}")
        raise


def generate_system_health_report(**context) -> Dict[str, Any]:
    """Generate comprehensive system health report."""
    try:
        ti = context['ti']
        
        # Collect data from all maintenance tasks
        resource_data = ti.xcom_pull(task_ids='check_resource_usage')
        cleanup_data = ti.xcom_pull(task_ids='cleanup_worktrees')
        archive_data = ti.xcom_pull(task_ids='archive_agents')
        rebalance_data = ti.xcom_pull(task_ids='rebalance_allocation')
        
        # Calculate system health metrics
        resource_usage = resource_data['resource_usage']
        
        health_score = 1.0
        health_factors = []
        
        # Penalize high resource usage
        if resource_usage['cpu_usage'] > 0.8:
            health_score -= 0.2
            health_factors.append("high_cpu_usage")
            
        if resource_usage['memory_usage'] > 0.8:
            health_score -= 0.2
            health_factors.append("high_memory_usage")
            
        if resource_usage['disk_usage'] > 0.8:
            health_score -= 0.1  # Less critical since we can clean up
            health_factors.append("high_disk_usage")
        
        # Credit cleanup actions
        if cleanup_data.get('space_freed_gb', 0) > 0:
            health_score += 0.1
            health_factors.append("cleanup_performed")
        
        health_score = max(0.0, min(1.0, health_score))  # Clamp to [0,1]
        
        # Determine health status
        if health_score >= 0.8:
            health_status = "healthy"
        elif health_score >= 0.6:
            health_status = "warning"
        else:
            health_status = "critical"
        
        health_report = {
            "health_score": health_score,
            "health_status": health_status,
            "health_factors": health_factors,
            "system_metrics": {
                "cpu_usage": resource_usage['cpu_usage'],
                "memory_usage": resource_usage['memory_usage'],
                "disk_usage": resource_usage['disk_usage'],
                "active_agents": resource_usage['active_agents'],
                "worktree_count": resource_usage['worktree_count']
            },
            "maintenance_summary": {
                "worktrees_cleaned": cleanup_data.get('worktrees_cleaned', 0),
                "space_freed_gb": cleanup_data.get('space_freed_gb', 0.0),
                "agents_archived": len(archive_data.get('agents_archived', [])),
                "agents_rebalanced": rebalance_data.get('agents_rebalanced', 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"System health report generated: {health_report}")
        return health_report
        
    except Exception as e:
        error_context = ErrorContext(
            error_type="HealthReportError",
            error_message=str(e),
            task_id="generate_system_health_report",
            remediation_steps=[
                "Check data availability from maintenance tasks",
                "Verify health calculation logic",
                "Review report generation process"
            ]
        )
        logger.error(f"Health report generation failed: {error_context.to_dict()}")
        raise


# Create the DAG
dean_system_maintenance_dag = DAG(
    'dean_system_maintenance',
    default_args=DEFAULT_ARGS,
    description='DEAN System Maintenance and Resource Management',
    schedule_interval=timedelta(hours=6),  # Run every 6 hours
    catchup=False,
    max_active_runs=1,
    tags=['dean', 'maintenance', 'cleanup'],
    params={
        'cleanup_age_hours': 24,
        'resource_threshold': 0.8,
        'force_cleanup': False,
        'archive_agents': True
    }
)

# Task definitions
check_resources_task = PythonOperator(
    task_id='check_resource_usage',
    python_callable=check_resource_usage,
    dag=dean_system_maintenance_dag,
    doc_md="""
    ## Check Resource Usage
    
    Monitors system resource usage including CPU, memory, disk space,
    and git worktree count to determine if maintenance is needed.
    """
)

# Create task group for cleanup operations
with TaskGroup(group_id='cleanup_operations', dag=dean_system_maintenance_dag) as cleanup_group:
    
    cleanup_worktrees_task = PythonOperator(
        task_id='cleanup_worktrees',
        python_callable=cleanup_worktrees,
        doc_md="""
        ## Cleanup Git Worktrees
        
        Removes old git worktrees that are no longer in use to free disk space
        and reduce system resource consumption.
        """
    )
    
    archive_agents_task = PythonOperator(
        task_id='archive_agents',
        python_callable=archive_agents,
        doc_md="""
        ## Archive Inactive Agents
        
        Archives agents that have been inactive for extended periods to
        free system resources while preserving their data.
        """
    )

rebalance_task = PythonOperator(
    task_id='rebalance_allocation',
    python_callable=rebalance_allocation,
    dag=dean_system_maintenance_dag,
    doc_md="""
    ## Rebalance Resource Allocation
    
    Redistributes system resources among active agents based on
    freed resources from cleanup and archival operations.
    """
)

health_report_task = PythonOperator(
    task_id='generate_system_health_report',
    python_callable=generate_system_health_report,
    dag=dean_system_maintenance_dag,
    trigger_rule='all_done',
    doc_md="""
    ## Generate System Health Report
    
    Creates a comprehensive health report including resource usage,
    maintenance actions performed, and overall system status.
    """
)

# Task dependencies
check_resources_task >> cleanup_group >> rebalance_task >> health_report_task

# Expose DAG for import
locals()['dean_system_maintenance_dag'] = dean_system_maintenance_dag
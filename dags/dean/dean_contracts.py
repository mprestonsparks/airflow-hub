"""
DEAN DAG Contracts and Data Models.

This module defines the input/output contracts for DEAN Airflow DAGs,
implementing contract-first development principles.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TaskStatus(Enum):
    """Status enumeration for task execution."""
    PENDING = "pending"
    RUNNING = "running" 
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class EvolutionRule(Enum):
    """Cellular automata evolution rules."""
    RULE_110 = "rule_110"  # Create improved neighbors
    RULE_30 = "rule_30"    # Fork into parallel worktrees
    RULE_90 = "rule_90"    # Abstract patterns
    RULE_184 = "rule_184"  # Learn from neighbors
    RULE_1 = "rule_1"      # Recurse to higher abstraction


# Evolution DAG Contracts
@dataclass
class EvolutionInput:
    """Input contract for agent evolution DAG."""
    population_size: int = field(default=10)
    cycles: int = field(default=3)
    environment_params: Dict[str, Any] = field(default_factory=dict)
    token_budget: int = field(default=1000)
    rules_enabled: List[EvolutionRule] = field(default_factory=lambda: list(EvolutionRule))
    
    def __post_init__(self):
        """Validate input parameters."""
        if not 2 <= self.population_size <= 100:
            raise ValueError(f"Population size must be 2-100, got {self.population_size}")
        if not 1 <= self.cycles <= 10:
            raise ValueError(f"Cycles must be 1-10, got {self.cycles}")
        if not 100 <= self.token_budget <= 100000:
            raise ValueError(f"Token budget must be 100-100000, got {self.token_budget}")


@dataclass  
class EvolutionOutput:
    """Output contract for agent evolution DAG."""
    agents_evolved: List[str] = field(default_factory=list)
    tokens_consumed: int = 0
    efficiency_gained: float = 0.0
    patterns_discovered: List[str] = field(default_factory=list)
    rules_applied: List[str] = field(default_factory=list)
    children_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    
    def success_rate(self) -> float:
        """Calculate success rate of evolution."""
        total_attempts = len(self.agents_evolved) + len(self.errors)
        if total_attempts == 0:
            return 0.0
        return len(self.agents_evolved) / total_attempts


# Population Management DAG Contracts  
@dataclass
class PopulationInput:
    """Input contract for population management DAG."""
    target_diversity: float = field(default=0.3)
    max_population: int = field(default=50)
    convergence_threshold: float = field(default=0.9)
    min_population: int = field(default=2)
    diversity_enforcement: bool = field(default=True)
    
    def __post_init__(self):
        """Validate input parameters."""
        if not 0.1 <= self.target_diversity <= 1.0:
            raise ValueError(f"Target diversity must be 0.1-1.0, got {self.target_diversity}")
        if not 2 <= self.max_population <= 500:
            raise ValueError(f"Max population must be 2-500, got {self.max_population}")
        if not 0.8 <= self.convergence_threshold <= 1.0:
            raise ValueError(f"Convergence threshold must be 0.8-1.0, got {self.convergence_threshold}")
        if self.min_population >= self.max_population:
            raise ValueError("Min population must be less than max population")


@dataclass
class PopulationOutput:
    """Output contract for population management DAG."""
    diversity_score: float = 0.0
    agents_created: List[str] = field(default_factory=list)
    agents_retired: List[str] = field(default_factory=list)
    rebalancing_actions: List[str] = field(default_factory=list)
    population_health: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    def net_population_change(self) -> int:
        """Calculate net change in population."""
        return len(self.agents_created) - len(self.agents_retired)


# System Maintenance DAG Contracts
@dataclass  
class MaintenanceInput:
    """Input contract for system maintenance DAG."""
    cleanup_age_hours: int = field(default=24)
    resource_threshold: float = field(default=0.8)
    force_cleanup: bool = field(default=False)
    archive_agents: bool = field(default=True)
    
    def __post_init__(self):
        """Validate input parameters."""
        if not 1 <= self.cleanup_age_hours <= 168:  # 1 hour to 1 week
            raise ValueError(f"Cleanup age must be 1-168 hours, got {self.cleanup_age_hours}")
        if not 0.5 <= self.resource_threshold <= 0.95:
            raise ValueError(f"Resource threshold must be 0.5-0.95, got {self.resource_threshold}")


@dataclass
class MaintenanceOutput:
    """Output contract for system maintenance DAG."""
    worktrees_cleaned: int = 0
    disk_space_freed_gb: float = 0.0
    agents_archived: List[str] = field(default_factory=list)
    system_health: Dict[str, float] = field(default_factory=dict)
    cleanup_actions: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def cleanup_efficiency(self) -> float:
        """Calculate cleanup efficiency score."""
        if self.worktrees_cleaned == 0:
            return 0.0
        return self.disk_space_freed_gb / self.worktrees_cleaned


# Task-level contracts
class TaskContract(BaseModel):
    """Base contract for individual DAG tasks."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current task status")
    start_time: Optional[datetime] = Field(None, description="Task start time")
    end_time: Optional[datetime] = Field(None, description="Task end time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, ge=0, le=3, description="Number of retries")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """Validate task ID format."""
        if not v or len(v) < 3:
            raise ValueError("Task ID must be at least 3 characters")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Task ID must contain only alphanumeric characters, hyphens, and underscores")
        return v
    
    def duration_seconds(self) -> float:
        """Calculate task duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class EvolutionTaskContract(TaskContract):
    """Contract for evolution-specific tasks."""
    agent_id: str = Field(..., description="Target agent ID")
    rule_applied: Optional[EvolutionRule] = Field(None, description="CA rule applied")
    tokens_used: int = Field(0, ge=0, description="Tokens consumed")
    efficiency_change: float = Field(0.0, description="Change in efficiency")
    
    
class PopulationTaskContract(TaskContract):
    """Contract for population management tasks."""
    population_before: int = Field(0, ge=0, description="Population size before task")
    population_after: int = Field(0, ge=0, description="Population size after task")
    diversity_before: float = Field(0.0, ge=0.0, le=1.0, description="Diversity before task")
    diversity_after: float = Field(0.0, ge=0.0, le=1.0, description="Diversity after task")


class MaintenanceTaskContract(TaskContract):
    """Contract for maintenance tasks."""
    resources_before: Dict[str, float] = Field(default_factory=dict, description="Resource usage before")
    resources_after: Dict[str, float] = Field(default_factory=dict, description="Resource usage after")
    items_processed: int = Field(0, ge=0, description="Number of items processed")


# DAG-level contracts
class DAGContract(BaseModel):
    """Base contract for DAG execution."""
    dag_id: str = Field(..., description="DAG identifier")
    run_id: str = Field(..., description="DAG run identifier")
    execution_date: datetime = Field(..., description="DAG execution date")
    tasks: List[TaskContract] = Field(default_factory=list, description="Task execution details")
    overall_status: TaskStatus = Field(TaskStatus.PENDING, description="Overall DAG status")
    total_duration_seconds: float = Field(0.0, ge=0.0, description="Total execution time")
    
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.tasks:
            return 0.0
        successful_tasks = sum(1 for task in self.tasks if task.status == TaskStatus.SUCCESS)
        return successful_tasks / len(self.tasks)
    
    def failed_tasks(self) -> List[TaskContract]:
        """Get list of failed tasks."""
        return [task for task in self.tasks if task.status == TaskStatus.FAILED]


# Property validation contracts
class SystemPropertyContract:
    """Contract for system properties that must be maintained."""
    
    @staticmethod
    def validate_population_bounds(current_pop: int, min_pop: int, max_pop: int) -> bool:
        """Validate population stays within bounds."""
        return min_pop <= current_pop <= max_pop
    
    @staticmethod
    def validate_token_conservation(allocated: int, consumed: int) -> bool:
        """Validate token budget conservation."""
        return consumed <= allocated
    
    @staticmethod
    def validate_resource_limits(usage: Dict[str, float], limits: Dict[str, float]) -> bool:
        """Validate resource usage stays within limits."""
        for resource, current_usage in usage.items():
            if resource in limits and current_usage > limits[resource]:
                return False
        return True
    
    @staticmethod
    def validate_diversity_maintenance(diversity: float, threshold: float) -> bool:
        """Validate diversity stays above threshold."""
        return diversity >= threshold
    
    @staticmethod
    def validate_data_integrity(before_count: int, after_count: int, created: int, deleted: int) -> bool:
        """Validate data integrity through operations."""
        expected_after = before_count + created - deleted
        return after_count == expected_after


# Error handling contracts
@dataclass
class ErrorContext:
    """Context information for error handling."""
    error_type: str
    error_message: str
    task_id: str
    agent_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    remediation_steps: List[str] = field(default_factory=list)
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "remediation_steps": self.remediation_steps,
            "error_code": self.error_code
        }


# SLA contracts
@dataclass
class SLAContract:
    """Service Level Agreement contracts for DAG execution."""
    max_execution_time_minutes: int = 15
    max_task_retries: int = 3
    required_success_rate: float = 0.95
    max_memory_usage_gb: float = 2.0
    max_cpu_usage_percent: float = 80.0
    
    def validate_execution_time(self, actual_minutes: float) -> bool:
        """Validate execution time meets SLA."""
        return actual_minutes <= self.max_execution_time_minutes
    
    def validate_success_rate(self, actual_rate: float) -> bool:
        """Validate success rate meets SLA."""
        return actual_rate >= self.required_success_rate
    
    def validate_resource_usage(self, memory_gb: float, cpu_percent: float) -> bool:
        """Validate resource usage meets SLA."""
        return memory_gb <= self.max_memory_usage_gb and cpu_percent <= self.max_cpu_usage_percent
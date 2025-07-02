"""
DEAN Agent Evolution Plugin for Apache Airflow.
Provides custom operators for managing DEAN agent lifecycle.
"""

from airflow.plugins_manager import AirflowPlugin
from agent_evolution.operators.agent_spawn_operator import AgentSpawnOperator
from agent_evolution.operators.agent_evolution_operator import AgentEvolutionOperator

class DEANAgentEvolutionPlugin(AirflowPlugin):
    """Plugin for DEAN agent evolution operators."""
    name = "dean_agent_evolution"
    operators = [AgentSpawnOperator, AgentEvolutionOperator]
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
"""
Analytics-specific operators for the analytics project.
"""

from plugins.project_analytics.operators.data_quality_operator import DataQualityOperator
from plugins.project_analytics.operators.ml_prediction_operator import MLPredictionOperator

__all__ = ['DataQualityOperator', 'MLPredictionOperator']

"""
ML prediction operator for running machine learning predictions.
"""

from airflow.utils.decorators import apply_defaults
from plugins.common.operators.base_operator import BaseDataOperator
import logging
import pandas as pd
import numpy as np
import os
import pickle
import json


class MLPredictionOperator(BaseDataOperator):
    """
    Operator for running machine learning predictions on datasets.
    
    This operator loads a trained ML model and runs predictions on input data,
    then saves the results to a specified location.
    
    Args:
        conn_id (str): Connection ID for the data source.
        model_path (str): Path to the saved ML model file.
        input_query (str): SQL query to fetch input data.
        output_table (str): Table name to save prediction results.
        features (list): List of feature column names.
        id_column (str): Name of the ID column.
        prediction_column (str, optional): Name for the prediction column. Defaults to 'prediction'.
        **kwargs: Additional arguments passed to the BaseDataOperator.
    """
    
    template_fields = ('model_path', 'input_query', 'output_table')
    
    @apply_defaults
    def __init__(
        self,
        conn_id,
        model_path,
        input_query,
        output_table,
        features,
        id_column,
        prediction_column='prediction',
        **kwargs
    ):
        super().__init__(conn_id=conn_id, **kwargs)
        self.model_path = model_path
        self.input_query = input_query
        self.output_table = output_table
        self.features = features
        self.id_column = id_column
        self.prediction_column = prediction_column
    
    def execute(self, context):
        """
        Execute the ML prediction.
        
        Args:
            context (dict): Airflow context dictionary.
            
        Returns:
            dict: Results of the prediction operation.
        """
        self.log.info(f"Running ML predictions using model: {self.model_path}")
        
        # Get database hook
        from plugins.common.hooks.database_hook import DatabaseHook
        hook = DatabaseHook(self.conn_id)
        
        # Fetch input data
        self.log.info(f"Fetching input data with query: {self.input_query}")
        results = hook.run_query(self.input_query)
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        if df.empty:
            message = "No input data found for prediction"
            self.log.warning(message)
            return {"success": False, "message": message}
        
        # Validate features exist in the dataset
        missing_features = [f for f in self.features if f not in df.columns]
        if missing_features:
            message = f"Missing features in input data: {missing_features}"
            self.log.error(message)
            raise ValueError(message)
        
        # Load the ML model
        try:
            self.log.info(f"Loading model from {self.model_path}")
            with open(self.model_path, 'rb') as model_file:
                model = pickle.load(model_file)
        except Exception as e:
            message = f"Error loading model: {str(e)}"
            self.log.error(message)
            raise ValueError(message)
        
        # Extract features for prediction
        X = df[self.features]
        
        # Run prediction
        try:
            self.log.info("Running predictions")
            predictions = model.predict(X)
            
            # Add predictions to DataFrame
            df[self.prediction_column] = predictions
            
            # For classification models, add probability scores if available
            if hasattr(model, 'predict_proba'):
                try:
                    probabilities = model.predict_proba(X)
                    # For binary classification, just store probability of positive class
                    if probabilities.shape[1] == 2:
                        df['probability'] = probabilities[:, 1]
                    # For multi-class, store all probabilities as JSON
                    else:
                        class_names = getattr(model, 'classes_', range(probabilities.shape[1]))
                        df['probabilities'] = [
                            json.dumps(dict(zip(class_names, probs)))
                            for probs in probabilities
                        ]
                except Exception as e:
                    self.log.warning(f"Could not generate probability scores: {str(e)}")
        
        except Exception as e:
            message = f"Error during prediction: {str(e)}"
            self.log.error(message)
            raise ValueError(message)
        
        # Save predictions to output table
        try:
            # Convert DataFrame to list of dictionaries
            prediction_records = df.to_dict('records')
            
            # Prepare SQL for inserting predictions
            columns = list(prediction_records[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_str = ', '.join(columns)
            
            # Create table if it doesn't exist
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.output_table} (
                {', '.join([f"{col} VARCHAR(255)" for col in columns])}
            )
            """
            
            # Execute create table
            hook.execute_query(create_table_sql)
            
            # Insert predictions
            insert_sql = f"""
            INSERT INTO {self.output_table} ({column_str})
            VALUES ({placeholders})
            """
            
            # Execute batch insert
            for record in prediction_records:
                values = [record[col] for col in columns]
                hook.execute_query(insert_sql, values)
            
            self.log.info(f"Saved {len(prediction_records)} predictions to {self.output_table}")
        
        except Exception as e:
            message = f"Error saving predictions: {str(e)}"
            self.log.error(message)
            raise ValueError(message)
        
        return {
            "success": True,
            "records_processed": len(df),
            "output_table": self.output_table
        }
    
    def _get_model_metadata(self, model):
        """
        Extract metadata from the ML model.
        
        Args:
            model: The loaded ML model.
            
        Returns:
            dict: Model metadata.
        """
        metadata = {
            "model_type": type(model).__name__
        }
        
        # Extract feature importances if available
        if hasattr(model, 'feature_importances_'):
            feature_importances = dict(zip(self.features, model.feature_importances_))
            metadata["feature_importances"] = feature_importances
        
        # Extract coefficients for linear models
        elif hasattr(model, 'coef_'):
            if len(model.coef_.shape) == 1:
                coefficients = dict(zip(self.features, model.coef_))
                metadata["coefficients"] = coefficients
            else:
                # For multi-class models
                metadata["coefficients"] = "Multi-class coefficients available"
        
        return metadata

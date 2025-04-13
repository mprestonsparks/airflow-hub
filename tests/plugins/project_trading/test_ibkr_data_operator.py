"""
Tests for the IBKRDataOperator.

This module contains unit tests for the IBKRDataOperator to ensure
it correctly extracts and processes trading data.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from plugins.project_trading.operators.ibkr_data_operator import IBKRDataOperator
from datetime import datetime


class TestIBKRDataOperator:
    """Test suite for IBKRDataOperator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.conn_id = 'project_trading_ibkr_test'
        self.data_types = ['trades', 'positions']
        self.start_date = '2023-01-01'
        self.end_date = '2023-01-02'
        self.output_path = '/tmp/test_output'
        
        # Create operator instance
        self.operator = IBKRDataOperator(
            task_id='test_extract',
            conn_id=self.conn_id,
            data_types=self.data_types,
            start_date=self.start_date,
            end_date=self.end_date,
            output_path=self.output_path
        )
        
        # Mock Airflow context
        self.context = {
            'execution_date': datetime(2023, 1, 1),
            'next_execution_date': datetime(2023, 1, 2)
        }
    
    @patch('plugins.project_trading.operators.ibkr_data_operator.BaseHook')
    def test_init(self, mock_base_hook):
        """Test operator initialization."""
        # Setup mock
        mock_connection = MagicMock()
        mock_base_hook.get_connection.return_value = mock_connection
        
        # Assert operator attributes
        assert self.operator.conn_id == self.conn_id
        assert self.operator.data_types == self.data_types
        assert self.operator.start_date == self.start_date
        assert self.operator.end_date == self.end_date
        assert self.operator.output_path == self.output_path
    
    @patch('plugins.project_trading.operators.ibkr_data_operator.BaseHook')
    @patch('plugins.project_trading.operators.ibkr_data_operator.os')
    def test_execute(self, mock_os, mock_base_hook):
        """Test execute method."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection.password = 'api_key'
        mock_connection.login = 'account_id'
        mock_connection.host = 'api_url'
        mock_base_hook.get_connection.return_value = mock_connection
        
        # Mock the extract methods
        with patch.object(self.operator, '_extract_trades') as mock_extract_trades, \
             patch.object(self.operator, '_extract_positions') as mock_extract_positions, \
             patch.object(self.operator, '_save_data') as mock_save_data:
            
            # Setup return values for mocks
            mock_extract_trades.return_value = pd.DataFrame({'trade_id': [1, 2], 'amount': [100, 200]})
            mock_extract_positions.return_value = pd.DataFrame({'symbol': ['AAPL', 'MSFT'], 'quantity': [10, 20]})
            
            # Execute the operator
            result = self.operator.execute(self.context)
            
            # Verify the correct methods were called
            mock_extract_trades.assert_called_once()
            mock_extract_positions.assert_called_once()
            
            # Verify results
            assert 'trades' in result
            assert 'positions' in result
            assert len(result['trades']) == 2
            assert len(result['positions']) == 2
            
            # Verify save was called for each data type
            assert mock_save_data.call_count == 2
    
    @patch('plugins.project_trading.operators.ibkr_data_operator.BaseHook')
    def test_extract_trades(self, mock_base_hook):
        """Test _extract_trades method."""
        # Call the method directly
        trades = self.operator._extract_trades('api_url', 'api_key', 'account_id', 
                                              datetime(2023, 1, 1), datetime(2023, 1, 2))
        
        # Verify result
        assert isinstance(trades, pd.DataFrame)
        assert not trades.empty
        assert 'symbol' in trades.columns
        assert 'quantity' in trades.columns
        assert 'price' in trades.columns
    
    @patch('plugins.project_trading.operators.ibkr_data_operator.BaseHook')
    def test_extract_positions(self, mock_base_hook):
        """Test _extract_positions method."""
        # Call the method directly
        positions = self.operator._extract_positions('api_url', 'api_key', 'account_id')
        
        # Verify result
        assert isinstance(positions, pd.DataFrame)
        assert not positions.empty
        assert 'symbol' in positions.columns
        assert 'quantity' in positions.columns
        assert 'market_value' in positions.columns
    
    @patch('plugins.project_trading.operators.ibkr_data_operator.os')
    @patch('plugins.project_trading.operators.ibkr_data_operator.BaseHook')
    def test_save_data(self, mock_base_hook, mock_os):
        """Test _save_data method."""
        # Setup test data
        test_df = pd.DataFrame({'symbol': ['AAPL', 'MSFT'], 'price': [150.0, 250.0]})
        
        # Call the method
        with patch.object(pd.DataFrame, 'to_csv') as mock_to_csv:
            self.operator._save_data(test_df, 'test_data')
            
            # Verify directory was created
            mock_os.makedirs.assert_called_once_with(self.output_path, exist_ok=True)
            
            # Verify CSV was saved
            mock_to_csv.assert_called_once()

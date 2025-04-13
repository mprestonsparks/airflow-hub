"""
Interactive Brokers data operator for extracting trading data.
"""

from airflow.utils.decorators import apply_defaults
from plugins.common.operators.base_operator import BaseDataOperator
import logging
import pandas as pd
import os
from datetime import datetime, timedelta


class IBKRDataOperator(BaseDataOperator):
    """
    Operator for extracting data from Interactive Brokers.
    
    This operator connects to Interactive Brokers API and extracts trading data
    such as trades, positions, market data, etc.
    
    Args:
        conn_id (str): Connection ID for IBKR. Should follow project naming convention.
        data_types (list): List of data types to extract (trades, positions, etc.).
        start_date (str or datetime, optional): Start date for data extraction.
        end_date (str or datetime, optional): End date for data extraction.
        output_path (str, optional): Path to save extracted data.
        **kwargs: Additional arguments passed to the BaseDataOperator.
    """
    
    template_fields = ('start_date', 'end_date', 'output_path')
    
    @apply_defaults
    def __init__(
        self,
        conn_id,
        data_types,
        start_date=None,
        end_date=None,
        output_path=None,
        **kwargs
    ):
        super().__init__(conn_id=conn_id, **kwargs)
        self.data_types = data_types
        self.start_date = start_date
        self.end_date = end_date
        self.output_path = output_path
        self.log = logging.getLogger(__name__)
    
    def execute(self, context):
        """
        Execute the data extraction from Interactive Brokers.
        
        Args:
            context (dict): Airflow context dictionary.
            
        Returns:
            dict: Dictionary containing the extracted data.
        """
        self.log.info(f"Extracting IBKR data for types: {self.data_types}")
        
        # Handle date parameters
        if self.start_date is None:
            # Default to yesterday if not specified
            self.start_date = context['execution_date'].strftime('%Y-%m-%d')
        
        if self.end_date is None:
            # Default to today if not specified
            self.end_date = context['next_execution_date'].strftime('%Y-%m-%d')
        
        # Convert string dates to datetime if needed
        if isinstance(self.start_date, str):
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        else:
            start_date = self.start_date
            
        if isinstance(self.end_date, str):
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        else:
            end_date = self.end_date
        
        # Get connection details
        connection = self.get_connection(self.conn_id)
        
        # Extract API credentials from connection
        api_key = connection.password
        account_id = connection.login
        api_url = connection.host
        
        # Initialize results dictionary
        results = {}
        
        # Process each requested data type
        for data_type in self.data_types:
            self.log.info(f"Extracting {data_type} data")
            
            # Call appropriate method based on data type
            if data_type == 'trades':
                data = self._extract_trades(api_url, api_key, account_id, start_date, end_date)
            elif data_type == 'positions':
                data = self._extract_positions(api_url, api_key, account_id)
            elif data_type == 'market_data':
                data = self._extract_market_data(api_url, api_key, start_date, end_date)
            else:
                self.log.warning(f"Unknown data type: {data_type}")
                continue
            
            # Store results
            results[data_type] = data
            
            # Save to file if output path is specified
            if self.output_path:
                self._save_data(data, data_type)
        
        return results
    
    def _extract_trades(self, api_url, api_key, account_id, start_date, end_date):
        """
        Extract trades data from IBKR.
        
        In a real implementation, this would use the IBKR API client.
        For this example, we'll simulate the data.
        
        Returns:
            pandas.DataFrame: Trades data.
        """
        self.log.info(f"Extracting trades from {start_date} to {end_date}")
        
        # In a real implementation, this would use the IBKR API
        # For example:
        # from ibapi.client import EClient
        # from ibapi.wrapper import EWrapper
        # ... implement API client logic ...
        
        # For this example, we'll simulate the data
        trades = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate 3-5 trades per day
            import random
            num_trades = random.randint(3, 5)
            
            for i in range(num_trades):
                trade = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'symbol': random.choice(['AAPL', 'MSFT', 'GOOGL', 'AMZN']),
                    'quantity': random.randint(1, 100),
                    'price': round(random.uniform(100, 500), 2),
                    'side': random.choice(['BUY', 'SELL']),
                    'commission': round(random.uniform(1, 10), 2),
                    'trade_id': f"T{random.randint(10000, 99999)}"
                }
                trades.append(trade)
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(trades)
    
    def _extract_positions(self, api_url, api_key, account_id):
        """
        Extract current positions from IBKR.
        
        In a real implementation, this would use the IBKR API client.
        For this example, we'll simulate the data.
        
        Returns:
            pandas.DataFrame: Positions data.
        """
        self.log.info(f"Extracting current positions for account {account_id}")
        
        # Simulate position data
        import random
        
        positions = []
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'NFLX']
        
        for symbol in symbols:
            if random.random() > 0.3:  # 70% chance to have a position
                position = {
                    'symbol': symbol,
                    'quantity': random.randint(-100, 100),
                    'avg_price': round(random.uniform(100, 500), 2),
                    'market_price': round(random.uniform(100, 500), 2),
                    'market_value': 0,
                    'unrealized_pnl': 0
                }
                
                # Calculate derived values
                position['market_value'] = position['quantity'] * position['market_price']
                position['unrealized_pnl'] = position['market_value'] - (position['quantity'] * position['avg_price'])
                
                positions.append(position)
        
        return pd.DataFrame(positions)
    
    def _extract_market_data(self, api_url, api_key, start_date, end_date):
        """
        Extract market data from IBKR.
        
        In a real implementation, this would use the IBKR API client.
        For this example, we'll simulate the data.
        
        Returns:
            dict: Dictionary of DataFrames with market data by symbol.
        """
        self.log.info(f"Extracting market data from {start_date} to {end_date}")
        
        # Simulate market data
        import random
        import numpy as np
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        market_data = {}
        
        for symbol in symbols:
            # Generate daily OHLCV data
            dates = []
            current_date = start_date
            
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            
            # Start with a base price
            last_close = random.uniform(100, 500)
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                dates.append(date_str)
                
                # Generate OHLC with some randomness but maintaining a reasonable sequence
                daily_volatility = random.uniform(0.01, 0.03)
                open_price = last_close * (1 + random.uniform(-0.01, 0.01))
                close_price = open_price * (1 + random.uniform(-daily_volatility, daily_volatility))
                high_price = max(open_price, close_price) * (1 + random.uniform(0.001, 0.02))
                low_price = min(open_price, close_price) * (1 - random.uniform(0.001, 0.02))
                
                opens.append(round(open_price, 2))
                highs.append(round(high_price, 2))
                lows.append(round(low_price, 2))
                closes.append(round(close_price, 2))
                volumes.append(int(random.uniform(100000, 10000000)))
                
                last_close = close_price
                current_date += timedelta(days=1)
            
            # Create DataFrame for this symbol
            market_data[symbol] = pd.DataFrame({
                'date': dates,
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'volume': volumes
            })
        
        return market_data
    
    def _save_data(self, data, data_type):
        """
        Save extracted data to files.
        
        Args:
            data: Data to save (DataFrame or dict of DataFrames).
            data_type (str): Type of data being saved.
        """
        # Create output directory if it doesn't exist
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)
            
            # Format date for filename
            date_str = datetime.now().strftime('%Y%m%d')
            
            if isinstance(data, pd.DataFrame):
                # Save single DataFrame
                filename = os.path.join(self.output_path, f"{data_type}_{date_str}.csv")
                data.to_csv(filename, index=False)
                self.log.info(f"Saved {data_type} data to {filename}")
            
            elif isinstance(data, dict):
                # Save dictionary of DataFrames
                for key, df in data.items():
                    filename = os.path.join(self.output_path, f"{data_type}_{key}_{date_str}.csv")
                    df.to_csv(filename, index=False)
                    self.log.info(f"Saved {data_type} data for {key} to {filename}")
            
            else:
                self.log.warning(f"Unsupported data type for saving: {type(data)}")

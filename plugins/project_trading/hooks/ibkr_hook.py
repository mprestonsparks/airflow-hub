"""
Interactive Brokers hook for connecting to IBKR API.
"""

from airflow.hooks.base import BaseHook
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os


class IBKRHook(BaseHook):
    """
    Hook for connecting to Interactive Brokers API.
    
    This hook provides methods for interacting with the Interactive Brokers API
    for trading operations, market data retrieval, and account management.
    
    Args:
        conn_id (str): Connection ID for IBKR. Should follow project naming convention.
    """
    
    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id
        self.connection = self.get_connection(conn_id)
        self.log = logging.getLogger(__name__)
        
        # Extract connection details
        self.api_key = self.connection.password
        self.account_id = self.connection.login
        self.api_url = self.connection.host
        self.port = self.connection.port or 4001  # Default IB Gateway port
        
        # Extract additional parameters from extras
        self.extras = self.connection.extra_dejson
        self.client_id = self.extras.get('client_id', 0)
        self.read_only = self.extras.get('read_only', True)
        
        # Validate connection naming convention
        if not conn_id.startswith('project_trading_'):
            self.log.warning(
                f"Connection ID '{conn_id}' does not follow project naming convention: "
                "project_trading_*"
            )
    
    def get_client(self):
        """
        Get an IBKR API client connection.
        
        Returns real or mock client based on configuration.
        
        Returns:
            object: IBKR API client.
        """
        self.log.info(f"Connecting to IBKR API at {self.api_url}:{self.port}")
        
        # Check if we should use real or mock client
        use_mock = self.extras.get('use_mock', True)
        
        if use_mock:
            # Use mock client for testing
            self.log.info("Using mock IBKR client")
            return MockIBKRClient(
                api_url=self.api_url,
                port=self.port,
                api_key=self.api_key,
                account_id=self.account_id,
                client_id=self.client_id,
                read_only=self.read_only
            )
        else:
            # Use real IBKR client
            try:
                from project_trading.hooks.ibkr_api_client import RealIBKRClient
                self.log.info("Using real IBKR client")
                return RealIBKRClient(
                    host=self.api_url,
                    port=self.port,
                    client_id=self.client_id,
                    account=self.account_id
                )
            except ImportError as e:
                self.log.warning(f"Real IBKR client not available: {e}. Falling back to mock.")
                return MockIBKRClient(
                    api_url=self.api_url,
                    port=self.port,
                    api_key=self.api_key,
                    account_id=self.account_id,
                    client_id=self.client_id,
                    read_only=self.read_only
                )
        #         EClient.__init__(self, self)
        #         # Initialize client properties
        #
        # client = IBClient()
        # client.connect(self.api_url, self.port, self.client_id)
        # return client
        
        # For this example, we'll return a mock client
        return MockIBKRClient(
            api_url=self.api_url,
            port=self.port,
            api_key=self.api_key,
            account_id=self.account_id,
            client_id=self.client_id,
            read_only=self.read_only
        )
    
    def get_account_summary(self):
        """
        Get account summary information.
        
        Returns:
            dict: Account summary data.
        """
        client = self.get_client()
        try:
            return client.get_account_summary(self.account_id)
        finally:
            client.disconnect()
    
    def get_positions(self):
        """
        Get current positions for the account.
        
        Returns:
            pandas.DataFrame: Positions data.
        """
        client = self.get_client()
        try:
            return client.get_positions(self.account_id)
        finally:
            client.disconnect()
    
    def get_trades(self, start_date, end_date):
        """
        Get trades for a date range.
        
        Args:
            start_date (str or datetime): Start date.
            end_date (str or datetime): End date.
            
        Returns:
            pandas.DataFrame: Trades data.
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        client = self.get_client()
        try:
            return client.get_trades(self.account_id, start_date, end_date)
        finally:
            client.disconnect()
    
    def get_market_data(self, symbols, start_date, end_date, bar_size='1 day'):
        """
        Get historical market data for symbols.
        
        Args:
            symbols (list): List of symbols to get data for.
            start_date (str or datetime): Start date.
            end_date (str or datetime): End date.
            bar_size (str, optional): Bar size for data. Defaults to '1 day'.
            
        Returns:
            dict: Dictionary of DataFrames with market data by symbol.
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        client = self.get_client()
        try:
            return client.get_market_data(symbols, start_date, end_date, bar_size)
        finally:
            client.disconnect()
    
    def place_order(self, symbol, quantity, order_type, limit_price=None):
        """
        Place a trading order.
        
        Args:
            symbol (str): Symbol to trade.
            quantity (int): Quantity to trade (negative for sell).
            order_type (str): Type of order (MARKET, LIMIT, etc.).
            limit_price (float, optional): Limit price for limit orders.
            
        Returns:
            dict: Order confirmation.
            
        Raises:
            ValueError: If read_only is True.
        """
        if self.read_only:
            raise ValueError("Cannot place orders in read-only mode")
        
        client = self.get_client()
        try:
            return client.place_order(
                account_id=self.account_id,
                symbol=symbol,
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price
            )
        finally:
            client.disconnect()


class MockIBKRClient:
    """
    Mock IBKR client for demonstration purposes.
    
    In a real implementation, this would be replaced with the actual IBKR API client.
    """
    
    def __init__(self, api_url, port, api_key, account_id, client_id, read_only):
        self.api_url = api_url
        self.port = port
        self.api_key = api_key
        self.account_id = account_id
        self.client_id = client_id
        self.read_only = read_only
        self.log = logging.getLogger(__name__)
        self.log.info(f"Initialized mock IBKR client for account {account_id}")
    
    def disconnect(self):
        """Simulate disconnecting from the API."""
        self.log.info("Disconnected from IBKR API")
    
    def get_account_summary(self, account_id):
        """
        Simulate getting account summary.
        
        Returns:
            dict: Mock account summary.
        """
        import random
        
        self.log.info(f"Getting account summary for {account_id}")
        
        # Generate mock account data
        return {
            'NetLiquidation': round(random.uniform(100000, 500000), 2),
            'TotalCashValue': round(random.uniform(10000, 50000), 2),
            'AvailableFunds': round(random.uniform(10000, 50000), 2),
            'GrossPositionValue': round(random.uniform(50000, 450000), 2),
            'EquityWithLoanValue': round(random.uniform(100000, 500000), 2),
            'BuyingPower': round(random.uniform(200000, 1000000), 2),
            'Leverage': round(random.uniform(1.0, 2.0), 2),
            'Currency': 'USD'
        }
    
    def get_positions(self, account_id):
        """
        Simulate getting positions.
        
        Returns:
            pandas.DataFrame: Mock positions data.
        """
        import random
        
        self.log.info(f"Getting positions for {account_id}")
        
        # Generate mock position data
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
    
    def get_trades(self, account_id, start_date, end_date):
        """
        Simulate getting trades.
        
        Returns:
            pandas.DataFrame: Mock trades data.
        """
        import random
        
        self.log.info(f"Getting trades for {account_id} from {start_date} to {end_date}")
        
        # Generate mock trade data
        trades = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate 3-5 trades per day
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
    
    def get_market_data(self, symbols, start_date, end_date, bar_size):
        """
        Simulate getting market data.
        
        Returns:
            dict: Dictionary of DataFrames with mock market data by symbol.
        """
        import random
        
        self.log.info(f"Getting market data for {symbols} from {start_date} to {end_date}")
        
        # Generate mock market data
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
    
    def place_order(self, account_id, symbol, quantity, order_type, limit_price=None):
        """
        Simulate placing an order.
        
        Returns:
            dict: Mock order confirmation.
            
        Raises:
            ValueError: If read_only is True.
        """
        import random
        
        if self.read_only:
            raise ValueError("Cannot place orders in read-only mode")
        
        self.log.info(f"Placing {order_type} order for {quantity} {symbol}")
        
        # Generate mock order confirmation
        order_id = f"O{random.randint(10000, 99999)}"
        
        return {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'order_type': order_type,
            'limit_price': limit_price,
            'status': 'SUBMITTED',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

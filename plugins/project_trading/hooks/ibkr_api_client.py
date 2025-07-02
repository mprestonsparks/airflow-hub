#!/usr/bin/env python3
"""
Interactive Brokers API Client
Real implementation for IBKR data extraction and trading operations
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from decimal import Decimal

# IB API imports
try:
    from ib_insync import IB, Contract, Order, MarketOrder, LimitOrder, StopOrder, util
    IB_INSYNC_AVAILABLE = True
except ImportError:
    IB_INSYNC_AVAILABLE = False
    logging.warning("ib_insync not available. Install with: pip install ib_insync")

logger = logging.getLogger(__name__)


class IBKRConnectionError(Exception):
    """IBKR connection errors"""
    pass


class IBKRDataError(Exception):
    """IBKR data retrieval errors"""
    pass


class RealIBKRClient:
    """
    Real Interactive Brokers API client using ib_insync.
    Handles connection, data retrieval, and order management.
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,  # 7497 for TWS paper, 7496 for TWS live, 4002 for Gateway paper, 4001 for Gateway live
        client_id: int = 1,
        account: str = None
    ):
        """
        Initialize IBKR client.
        
        Args:
            host: TWS/Gateway host
            port: TWS/Gateway port
            client_id: Unique client ID
            account: Account ID (optional, will use primary if not specified)
        """
        if not IB_INSYNC_AVAILABLE:
            raise ImportError("ib_insync is required for real IBKR integration")
        
        self.host = host
        self.port = port
        self.client_id = client_id
        self.account = account
        self.ib = IB()
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to TWS/Gateway.
        
        Returns:
            True if connected successfully
        """
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.connected = True
            
            # Get account if not specified
            if not self.account and self.ib.managedAccounts():
                self.account = self.ib.managedAccounts()[0]
                logger.info(f"Using account: {self.account}")
            
            logger.info(f"Connected to IBKR at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {e}")
            self.connected = False
            raise IBKRConnectionError(f"Connection failed: {e}")
    
    def disconnect(self):
        """Disconnect from TWS/Gateway"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR")
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary including balances and positions.
        
        Returns:
            Dict with account information
        """
        if not self.connected:
            raise IBKRConnectionError("Not connected to IBKR")
        
        try:
            # Get account values
            account_values = self.ib.accountValues(self.account)
            account_summary = self.ib.accountSummary(self.account)
            
            # Parse values
            summary = {
                "account": self.account,
                "timestamp": datetime.now().isoformat(),
                "values": {},
                "positions": [],
                "orders": []
            }
            
            # Extract key values
            for av in account_values:
                if av.tag in ["NetLiquidation", "TotalCashValue", "GrossPositionValue", 
                             "BuyingPower", "AvailableFunds", "MaintMarginReq"]:
                    summary["values"][av.tag] = {
                        "value": float(av.value),
                        "currency": av.currency
                    }
            
            # Get positions
            positions = self.ib.positions(self.account)
            for pos in positions:
                summary["positions"].append({
                    "symbol": pos.contract.symbol,
                    "secType": pos.contract.secType,
                    "position": float(pos.position),
                    "avgCost": float(pos.avgCost),
                    "marketValue": float(pos.position * pos.avgCost)  # Simplified
                })
            
            # Get open orders
            orders = self.ib.openOrders()
            for order in orders:
                summary["orders"].append({
                    "orderId": order.orderId,
                    "symbol": order.contract.symbol,
                    "action": order.action,
                    "quantity": float(order.totalQuantity),
                    "orderType": order.orderType,
                    "status": order.status
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get account summary: {e}")
            raise IBKRDataError(f"Account summary failed: {e}")
    
    def get_market_data(
        self,
        symbol: str,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD",
        duration: str = "1 D",
        bar_size: str = "1 min"
    ) -> pd.DataFrame:
        """
        Get historical market data.
        
        Args:
            symbol: Ticker symbol
            sec_type: Security type (STK, OPT, FUT, etc.)
            exchange: Exchange (SMART for smart routing)
            currency: Currency
            duration: Duration string (e.g., "1 D", "1 W", "1 M")
            bar_size: Bar size (e.g., "1 min", "5 mins", "1 hour", "1 day")
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.connected:
            raise IBKRConnectionError("Not connected to IBKR")
        
        try:
            # Create contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = sec_type
            contract.exchange = exchange
            contract.currency = currency
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime="",  # Use current time
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow="TRADES",
                useRTH=True,
                formatDate=1
            )
            
            if not bars:
                raise IBKRDataError(f"No data returned for {symbol}")
            
            # Convert to DataFrame
            df = util.df(bars)
            df["symbol"] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            raise IBKRDataError(f"Market data failed: {e}")
    
    def get_realtime_data(
        self,
        symbols: List[str],
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get real-time market data for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            sec_type: Security type
            exchange: Exchange
            currency: Currency
            
        Returns:
            Dict mapping symbols to their real-time data
        """
        if not self.connected:
            raise IBKRConnectionError("Not connected to IBKR")
        
        realtime_data = {}
        
        try:
            for symbol in symbols:
                # Create contract
                contract = Contract()
                contract.symbol = symbol
                contract.secType = sec_type
                contract.exchange = exchange
                contract.currency = currency
                
                # Request market data
                ticker = self.ib.reqMktData(contract, "", False, False)
                self.ib.sleep(0.5)  # Wait for data
                
                realtime_data[symbol] = {
                    "bid": float(ticker.bid) if ticker.bid != -1 else None,
                    "ask": float(ticker.ask) if ticker.ask != -1 else None,
                    "last": float(ticker.last) if ticker.last != -1 else None,
                    "volume": int(ticker.volume) if ticker.volume != -1 else None,
                    "high": float(ticker.high) if ticker.high != -1 else None,
                    "low": float(ticker.low) if ticker.low != -1 else None,
                    "close": float(ticker.close) if ticker.close != -1 else None,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Cancel market data subscription
                self.ib.cancelMktData(contract)
            
            return realtime_data
            
        except Exception as e:
            logger.error(f"Failed to get real-time data: {e}")
            raise IBKRDataError(f"Real-time data failed: {e}")
    
    def place_order(
        self,
        symbol: str,
        action: str,  # BUY or SELL
        quantity: int,
        order_type: str = "MKT",  # MKT, LMT, STP
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            symbol: Ticker symbol
            action: BUY or SELL
            quantity: Number of shares/contracts
            order_type: Order type (MKT, LMT, STP)
            limit_price: Limit price for LMT orders
            stop_price: Stop price for STP orders
            sec_type: Security type
            exchange: Exchange
            currency: Currency
            
        Returns:
            Dict with order details
        """
        if not self.connected:
            raise IBKRConnectionError("Not connected to IBKR")
        
        try:
            # Create contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = sec_type
            contract.exchange = exchange
            contract.currency = currency
            
            # Create order based on type
            if order_type == "MKT":
                order = MarketOrder(action, quantity)
            elif order_type == "LMT":
                if limit_price is None:
                    raise ValueError("Limit price required for LMT orders")
                order = LimitOrder(action, quantity, limit_price)
            elif order_type == "STP":
                if stop_price is None:
                    raise ValueError("Stop price required for STP orders")
                order = StopOrder(action, quantity, stop_price)
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            # Place order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for order to be transmitted
            self.ib.sleep(1)
            
            return {
                "orderId": trade.order.orderId,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "orderType": order_type,
                "status": trade.orderStatus.status,
                "filled": trade.orderStatus.filled,
                "remaining": trade.orderStatus.remaining,
                "avgFillPrice": trade.orderStatus.avgFillPrice,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise IBKRDataError(f"Order placement failed: {e}")
    
    def cancel_order(self, order_id: int) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if not self.connected:
            raise IBKRConnectionError("Not connected to IBKR")
        
        try:
            # Find the order
            for trade in self.ib.openTrades():
                if trade.order.orderId == order_id:
                    self.ib.cancelOrder(trade.order)
                    logger.info(f"Cancelled order {order_id}")
                    return True
            
            logger.warning(f"Order {order_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_portfolio_metrics(self) -> Dict[str, Any]:
        """
        Calculate portfolio metrics including returns and risk.
        
        Returns:
            Dict with portfolio metrics
        """
        if not self.connected:
            raise IBKRConnectionError("Not connected to IBKR")
        
        try:
            # Get account data
            account_data = self.get_account_summary()
            positions = account_data["positions"]
            
            if not positions:
                return {
                    "total_value": 0,
                    "position_count": 0,
                    "metrics": {}
                }
            
            # Calculate basic metrics
            total_value = sum(p["marketValue"] for p in positions)
            position_count = len(positions)
            
            # Get historical data for each position to calculate returns
            returns = []
            for position in positions[:10]:  # Limit to avoid too many requests
                try:
                    df = self.get_market_data(
                        symbol=position["symbol"],
                        duration="1 M",
                        bar_size="1 day"
                    )
                    if len(df) > 1:
                        position_return = (df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]
                        returns.append(position_return)
                except:
                    continue
            
            # Calculate metrics
            metrics = {
                "total_value": total_value,
                "position_count": position_count,
                "average_return": sum(returns) / len(returns) if returns else 0,
                "return_volatility": pd.Series(returns).std() if len(returns) > 1 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio metrics: {e}")
            raise IBKRDataError(f"Portfolio metrics failed: {e}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


# Async wrapper for compatibility
class AsyncIBKRClient:
    """Async wrapper for IBKR client"""
    
    def __init__(self, *args, **kwargs):
        self.sync_client = RealIBKRClient(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
    
    async def connect(self) -> bool:
        return await self.loop.run_in_executor(None, self.sync_client.connect)
    
    async def disconnect(self):
        return await self.loop.run_in_executor(None, self.sync_client.disconnect)
    
    async def get_account_summary(self) -> Dict[str, Any]:
        return await self.loop.run_in_executor(None, self.sync_client.get_account_summary)
    
    async def get_market_data(self, *args, **kwargs) -> pd.DataFrame:
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync_client.get_market_data(*args, **kwargs)
        )
    
    async def get_realtime_data(self, *args, **kwargs) -> Dict[str, Dict[str, Any]]:
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync_client.get_realtime_data(*args, **kwargs)
        )
    
    async def place_order(self, *args, **kwargs) -> Dict[str, Any]:
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync_client.place_order(*args, **kwargs)
        )
    
    async def cancel_order(self, order_id: int) -> bool:
        return await self.loop.run_in_executor(
            None,
            lambda: self.sync_client.cancel_order(order_id)
        )
    
    async def get_portfolio_metrics(self) -> Dict[str, Any]:
        return await self.loop.run_in_executor(None, self.sync_client.get_portfolio_metrics)
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
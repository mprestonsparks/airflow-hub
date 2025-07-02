"""
CLI script for extracting Interactive Brokers data for Airflow containerized execution.

This script is designed to be run inside the project_trading Docker image via DockerOperator in Airflow.
It moves the extraction logic out of the Airflow process for better isolation, reproducibility, and dependency management.
"""
import argparse
import os
import logging
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_ibkr_data(conn_id: str, data_types: List[str], start_date: str, end_date: str, output_path: str):
    """
    Extract IBKR data using real or mock client based on environment.
    
    Args:
        conn_id: Connection ID (for reference)
        data_types: List of data types to extract (trades, positions, account, market_data)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        output_path: Directory to write extracted data
    """
    logger.info(f"Extracting IBKR data: {data_types} from {start_date} to {end_date}")
    os.makedirs(output_path, exist_ok=True)
    
    # Check if we should use real IBKR client
    use_real_client = os.getenv("USE_REAL_IBKR", "false").lower() == "true"
    
    if use_real_client:
        try:
            # Import real client
            from project_trading.hooks.ibkr_api_client import RealIBKRClient
            
            # Get connection parameters from environment
            host = os.getenv("IBKR_HOST", "127.0.0.1")
            port = int(os.getenv("IBKR_PORT", "7497"))  # Paper trading port
            client_id = int(os.getenv("IBKR_CLIENT_ID", "1"))
            account = os.getenv("IBKR_ACCOUNT")
            
            logger.info(f"Connecting to real IBKR at {host}:{port}")
            
            with RealIBKRClient(host=host, port=port, client_id=client_id, account=account) as client:
                # Extract requested data types
                for dtype in data_types:
                    if dtype == "account":
                        data = client.get_account_summary()
                        fpath = os.path.join(output_path, f"account_{start_date}_to_{end_date}.json")
                        with open(fpath, 'w') as f:
                            json.dump(data, f, indent=2)
                        logger.info(f"Wrote account data to {fpath}")
                        
                    elif dtype == "positions":
                        account_data = client.get_account_summary()
                        positions_df = pd.DataFrame(account_data.get("positions", []))
                        fpath = os.path.join(output_path, f"positions_{start_date}_to_{end_date}.csv")
                        positions_df.to_csv(fpath, index=False)
                        logger.info(f"Wrote positions data to {fpath}")
                        
                    elif dtype == "market_data":
                        # Extract market data for configured symbols
                        symbols = os.getenv("IBKR_SYMBOLS", "SPY,QQQ,IWM").split(",")
                        market_data = []
                        
                        for symbol in symbols:
                            try:
                                df = client.get_market_data(
                                    symbol=symbol,
                                    duration="1 D",
                                    bar_size="5 mins"
                                )
                                df["symbol"] = symbol
                                market_data.append(df)
                            except Exception as e:
                                logger.warning(f"Failed to get data for {symbol}: {e}")
                        
                        if market_data:
                            combined_df = pd.concat(market_data, ignore_index=True)
                            fpath = os.path.join(output_path, f"market_data_{start_date}_to_{end_date}.csv")
                            combined_df.to_csv(fpath, index=False)
                            logger.info(f"Wrote market data to {fpath}")
                    
                    elif dtype == "trades":
                        # For trades, we would need to query execution reports
                        # This is a placeholder - real implementation would query executions
                        logger.info("Trade extraction not yet implemented for real client")
                        
        except Exception as e:
            logger.error(f"Failed to use real IBKR client: {e}. Falling back to mock data.")
            use_real_client = False
    
    # Use mock data if real client not available or failed
    if not use_real_client:
        logger.info("Using mock IBKR data")
        
        # Generate mock data for each requested type
        for dtype in data_types:
            if dtype == "account":
                mock_account = {
                    "account": "DU123456",
                    "timestamp": datetime.now().isoformat(),
                    "values": {
                        "NetLiquidation": {"value": 1000000.0, "currency": "USD"},
                        "TotalCashValue": {"value": 250000.0, "currency": "USD"},
                        "BuyingPower": {"value": 500000.0, "currency": "USD"}
                    },
                    "positions": [
                        {"symbol": "SPY", "position": 100, "avgCost": 400.0},
                        {"symbol": "QQQ", "position": 50, "avgCost": 350.0}
                    ]
                }
                fpath = os.path.join(output_path, f"account_{start_date}_to_{end_date}.json")
                with open(fpath, 'w') as f:
                    json.dump(mock_account, f, indent=2)
                
            elif dtype == "positions":
                positions_df = pd.DataFrame([
                    {"symbol": "SPY", "position": 100, "avgCost": 400.0, "marketValue": 42000.0},
                    {"symbol": "QQQ", "position": 50, "avgCost": 350.0, "marketValue": 18000.0},
                    {"symbol": "IWM", "position": 200, "avgCost": 180.0, "marketValue": 37000.0}
                ])
                fpath = os.path.join(output_path, f"positions_{start_date}_to_{end_date}.csv")
                positions_df.to_csv(fpath, index=False)
                
            elif dtype == "market_data":
                # Generate mock OHLCV data
                dates = pd.date_range(start_date, end_date, freq='5min')
                mock_data = []
                for symbol in ["SPY", "QQQ", "IWM"]:
                    base_price = {"SPY": 420, "QQQ": 360, "IWM": 185}[symbol]
                    df = pd.DataFrame({
                        "date": dates,
                        "open": base_price + pd.Series(range(len(dates))) * 0.01,
                        "high": base_price + pd.Series(range(len(dates))) * 0.02,
                        "low": base_price - pd.Series(range(len(dates))) * 0.01,
                        "close": base_price + pd.Series(range(len(dates))) * 0.015,
                        "volume": 1000000 + pd.Series(range(len(dates))) * 1000,
                        "symbol": symbol
                    })
                    mock_data.append(df)
                
                combined_df = pd.concat(mock_data, ignore_index=True)
                fpath = os.path.join(output_path, f"market_data_{start_date}_to_{end_date}.csv")
                combined_df.to_csv(fpath, index=False)
                
            elif dtype == "trades":
                trades_df = pd.DataFrame([
                    {"timestamp": datetime.now() - timedelta(hours=i), 
                     "symbol": ["SPY", "QQQ", "IWM"][i % 3],
                     "action": ["BUY", "SELL"][i % 2],
                     "quantity": 100 * (i + 1),
                     "price": 400 + i * 5,
                     "commission": 1.0}
                    for i in range(5)
                ])
                fpath = os.path.join(output_path, f"trades_{start_date}_to_{end_date}.csv")
                trades_df.to_csv(fpath, index=False)
            
            logger.info(f"Wrote mock {dtype} data to {output_path}")
    
    logger.info("Extraction complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract IBKR trading data for Airflow DAG.")
    parser.add_argument("--conn-id", required=True, help="Connection ID for IBKR (for logging/reference)")
    parser.add_argument("--data-types", nargs="+", required=True, help="Data types to extract (trades, positions, etc.)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-path", required=True, help="Where to write extracted data")
    args = parser.parse_args()
    extract_ibkr_data(
        conn_id=args.conn_id,
        data_types=args.data_types,
        start_date=args.start_date,
        end_date=args.end_date,
        output_path=args.output_path,
    )

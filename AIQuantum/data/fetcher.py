import ccxt
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import time
from ..utils.logger import get_logger

class DataFetcher:
    """
    Handles data fetching from various cryptocurrency exchanges.
    Supports both real-time and historical data retrieval.
    """
    
    def __init__(self, exchange_id: str = 'binanceus', config: Optional[Dict] = None):
        """
        Initialize the data fetcher with exchange configuration.
        
        Args:
            exchange_id: Exchange identifier (e.g., 'binanceus', 'kucoin')
            config: Exchange-specific configuration
        """
        self.logger = get_logger(__name__)
        self.exchange_id = exchange_id.lower()
        self.config = config or {}
        
        # BinanceUS specific configurations
        if self.exchange_id == 'binanceus':
            self.config.update({
                'enableRateLimit': True,
                'timeout': 30000,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True,
                    'recvWindow': 60000
                }
            })
        
        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            self.exchange = exchange_class(self.config)
            self.logger.info(f"Initialized {self.exchange_id} exchange")
            
            # Load markets for validation
            self.markets = self.exchange.load_markets()
            self.logger.info(f"Loaded {len(self.markets)} markets")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.exchange_id}: {str(e)}")
            raise
    
    def get_historical_data(self,
                          symbol: str,
                          timeframe: str = '1h',
                          since: Optional[Union[int, datetime]] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe for candles (e.g., '1h', '4h', '1d')
            since: Start time (timestamp or datetime)
            limit: Maximum number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Validate symbol format for BinanceUS
            if self.exchange_id == 'binanceus':
                if not self.validate_symbol(symbol):
                    raise ValueError(f"Invalid symbol format for BinanceUS: {symbol}")
            
            # Convert datetime to timestamp if needed
            if isinstance(since, datetime):
                since = int(since.timestamp() * 1000)
            
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            self.logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            raise
    
    def get_recent_trades(self,
                         symbol: str,
                         limit: int = 100) -> pd.DataFrame:
        """
        Fetch recent trades for a symbol.
        
        Args:
            symbol: Trading pair symbol
            limit: Maximum number of trades to fetch
            
        Returns:
            DataFrame with recent trades
        """
        try:
            # Validate symbol format for BinanceUS
            if self.exchange_id == 'binanceus':
                if not self.validate_symbol(symbol):
                    raise ValueError(f"Invalid symbol format for BinanceUS: {symbol}")
            
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error fetching recent trades for {symbol}: {str(e)}")
            raise
    
    def get_order_book(self,
                      symbol: str,
                      limit: int = 20) -> Dict:
        """
        Fetch current order book.
        
        Args:
            symbol: Trading pair symbol
            limit: Number of orders to fetch
            
        Returns:
            Dictionary with bids and asks
        """
        try:
            # Validate symbol format for BinanceUS
            if self.exchange_id == 'binanceus':
                if not self.validate_symbol(symbol):
                    raise ValueError(f"Invalid symbol format for BinanceUS: {symbol}")
            
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': pd.DataFrame(order_book['bids'], columns=['price', 'amount']),
                'asks': pd.DataFrame(order_book['asks'], columns=['price', 'amount'])
            }
        except Exception as e:
            self.logger.error(f"Error fetching order book for {symbol}: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Fetch current ticker information.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary with ticker information
        """
        try:
            # Validate symbol format for BinanceUS
            if self.exchange_id == 'binanceus':
                if not self.validate_symbol(symbol):
                    raise ValueError(f"Invalid symbol format for BinanceUS: {symbol}")
            
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            raise
    
    def get_markets(self) -> List[str]:
        """
        Get list of available markets.
        
        Returns:
            List of market symbols
        """
        try:
            return list(self.markets.keys())
        except Exception as e:
            self.logger.error(f"Error fetching markets: {str(e)}")
            raise
    
    def get_timeframes(self) -> List[str]:
        """
        Get list of available timeframes.
        
        Returns:
            List of timeframe strings
        """
        try:
            return list(self.exchange.timeframes.keys())
        except Exception as e:
            self.logger.error(f"Error fetching timeframes: {str(e)}")
            raise
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid for the exchange.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            True if symbol is valid
        """
        try:
            # BinanceUS specific validation
            if self.exchange_id == 'binanceus':
                # Check if symbol exists in markets
                if symbol not in self.markets:
                    return False
                
                # Check if trading is enabled
                market = self.markets[symbol]
                if not market.get('active', False):
                    return False
                
                # Check if spot trading is available
                if not market.get('spot', False):
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error validating symbol {symbol}: {str(e)}")
            return False
    
    def get_exchange_info(self) -> Dict:
        """
        Get exchange information and limits.
        
        Returns:
            Dictionary with exchange information
        """
        try:
            info = {
                'name': self.exchange.name,
                'timeframes': self.exchange.timeframes,
                'rateLimit': self.exchange.rateLimit,
                'has': self.exchange.has,
                'options': self.exchange.options
            }
            
            # Add BinanceUS specific information
            if self.exchange_id == 'binanceus':
                info.update({
                    'trading_fees': self.exchange.fetch_trading_fees(),
                    'withdrawal_fees': self.exchange.fetch_withdrawal_fees(),
                    'deposit_methods': self.exchange.fetch_deposit_methods(),
                })
            
            return info
        except Exception as e:
            self.logger.error(f"Error fetching exchange info: {str(e)}")
            raise 
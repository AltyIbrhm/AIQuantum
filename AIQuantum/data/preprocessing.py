import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from ..utils.logger import get_logger

class DataPreprocessor:
    """
    Handles data preprocessing and feature engineering.
    Supports various scaling methods and sequence generation for ML models.
    """
    
    def __init__(self):
        """
        Initialize the data preprocessor.
        """
        self.logger = get_logger(__name__)
        self.scalers: Dict[str, Union[MinMaxScaler, StandardScaler]] = {}
    
    def add_technical_indicators(self,
                               df: pd.DataFrame,
                               indicators: List[str] = None) -> pd.DataFrame:
        """
        Add technical indicators to the DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            indicators: List of indicators to add
            
        Returns:
            DataFrame with added indicators
        """
        try:
            if indicators is None:
                indicators = ['sma', 'ema', 'rsi', 'macd']
            
            df = df.copy()
            
            for indicator in indicators:
                if indicator == 'sma':
                    df['sma_20'] = df['close'].rolling(window=20).mean()
                    df['sma_50'] = df['close'].rolling(window=50).mean()
                elif indicator == 'ema':
                    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
                    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
                elif indicator == 'rsi':
                    delta = df['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['rsi'] = 100 - (100 / (1 + rs))
                elif indicator == 'macd':
                    exp1 = df['close'].ewm(span=12, adjust=False).mean()
                    exp2 = df['close'].ewm(span=26, adjust=False).mean()
                    df['macd'] = exp1 - exp2
                    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
                elif indicator == 'bollinger':
                    df['bb_middle'] = df['close'].rolling(window=20).mean()
                    df['bb_std'] = df['close'].rolling(window=20).std()
                    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
                    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
            
            self.logger.info(f"Added technical indicators: {indicators}")
            return df
        except Exception as e:
            self.logger.error(f"Error adding technical indicators: {str(e)}")
            raise
    
    def scale_data(self,
                  df: pd.DataFrame,
                  columns: List[str] = None,
                  method: str = 'minmax') -> pd.DataFrame:
        """
        Scale data using specified method.
        
        Args:
            df: DataFrame to scale
            columns: Columns to scale (default: all numeric columns)
            method: Scaling method ('minmax' or 'standard')
            
        Returns:
            Scaled DataFrame
        """
        try:
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            df_scaled = df.copy()
            
            for col in columns:
                if method == 'minmax':
                    scaler = MinMaxScaler()
                elif method == 'standard':
                    scaler = StandardScaler()
                else:
                    raise ValueError(f"Invalid scaling method: {method}")
                
                df_scaled[col] = scaler.fit_transform(df[[col]])
                self.scalers[col] = scaler
            
            self.logger.info(f"Scaled columns {columns} using {method} method")
            return df_scaled
        except Exception as e:
            self.logger.error(f"Error scaling data: {str(e)}")
            raise
    
    def inverse_scale(self,
                     df: pd.DataFrame,
                     columns: List[str] = None) -> pd.DataFrame:
        """
        Inverse transform scaled data.
        
        Args:
            df: Scaled DataFrame
            columns: Columns to inverse transform
            
        Returns:
            DataFrame with inverse transformed values
        """
        try:
            if columns is None:
                columns = list(self.scalers.keys())
            
            df_inverse = df.copy()
            
            for col in columns:
                if col in self.scalers:
                    df_inverse[col] = self.scalers[col].inverse_transform(df[[col]])
            
            self.logger.info(f"Inverse transformed columns: {columns}")
            return df_inverse
        except Exception as e:
            self.logger.error(f"Error inverse scaling data: {str(e)}")
            raise
    
    def create_sequences(self,
                        df: pd.DataFrame,
                        sequence_length: int,
                        target_col: str = 'close',
                        features: List[str] = None) -> tuple:
        """
        Create sequences for time series data.
        
        Args:
            df: DataFrame with features
            sequence_length: Length of input sequences
            target_col: Target column name
            features: List of feature columns to use
            
        Returns:
            Tuple of (X, y) arrays
        """
        try:
            if features is None:
                features = df.columns.tolist()
            
            data = df[features].values
            target = df[target_col].values
            
            X, y = [], []
            
            for i in range(len(data) - sequence_length):
                X.append(data[i:(i + sequence_length)])
                y.append(target[i + sequence_length])
            
            X = np.array(X)
            y = np.array(y)
            
            self.logger.info(f"Created sequences with length {sequence_length}")
            return X, y
        except Exception as e:
            self.logger.error(f"Error creating sequences: {str(e)}")
            raise
    
    def add_lag_features(self,
                        df: pd.DataFrame,
                        columns: List[str] = None,
                        lags: List[int] = None) -> pd.DataFrame:
        """
        Add lagged features to the DataFrame.
        
        Args:
            df: DataFrame to add lags to
            columns: Columns to create lags for
            lags: List of lag periods
            
        Returns:
            DataFrame with added lag features
        """
        try:
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if lags is None:
                lags = [1, 2, 3, 5, 10]
            
            df_lagged = df.copy()
            
            for col in columns:
                for lag in lags:
                    df_lagged[f'{col}_lag_{lag}'] = df[col].shift(lag)
            
            self.logger.info(f"Added lag features for columns: {columns}")
            return df_lagged
        except Exception as e:
            self.logger.error(f"Error adding lag features: {str(e)}")
            raise
    
    def add_rolling_features(self,
                           df: pd.DataFrame,
                           columns: List[str] = None,
                           windows: List[int] = None,
                           functions: List[str] = None) -> pd.DataFrame:
        """
        Add rolling window features to the DataFrame.
        
        Args:
            df: DataFrame to add rolling features to
            columns: Columns to create rolling features for
            windows: List of window sizes
            functions: List of functions to apply ('mean', 'std', 'min', 'max')
            
        Returns:
            DataFrame with added rolling features
        """
        try:
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if windows is None:
                windows = [5, 10, 20, 50]
            
            if functions is None:
                functions = ['mean', 'std', 'min', 'max']
            
            df_rolling = df.copy()
            
            for col in columns:
                for window in windows:
                    for func in functions:
                        if func == 'mean':
                            df_rolling[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
                        elif func == 'std':
                            df_rolling[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
                        elif func == 'min':
                            df_rolling[f'{col}_rolling_min_{window}'] = df[col].rolling(window=window).min()
                        elif func == 'max':
                            df_rolling[f'{col}_rolling_max_{window}'] = df[col].rolling(window=window).max()
            
            self.logger.info(f"Added rolling features for columns: {columns}")
            return df_rolling
        except Exception as e:
            self.logger.error(f"Error adding rolling features: {str(e)}")
            raise 
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import os
import glob
from pathlib import Path
from ..utils.logger import get_logger

class DataLoader:
    """
    Handles loading and managing local data files.
    Supports various file formats and data preprocessing.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the data loader with a data directory.
        
        Args:
            data_dir: Directory containing data files
        """
        self.logger = get_logger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Initialized DataLoader with directory: {data_dir}")
    
    def load_csv(self,
                filename: str,
                parse_dates: bool = True,
                index_col: Optional[str] = 'timestamp') -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Args:
            filename: Name of the CSV file
            parse_dates: Whether to parse dates
            index_col: Column to use as index
            
        Returns:
            DataFrame with loaded data
        """
        try:
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath, parse_dates=parse_dates, index_col=index_col)
            self.logger.info(f"Loaded {len(df)} rows from {filename}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading CSV {filename}: {str(e)}")
            raise
    
    def save_csv(self,
                df: pd.DataFrame,
                filename: str,
                index: bool = True) -> None:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Name of the output file
            index: Whether to save the index
        """
        try:
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=index)
            self.logger.info(f"Saved {len(df)} rows to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving CSV {filename}: {str(e)}")
            raise
    
    def load_parquet(self,
                    filename: str) -> pd.DataFrame:
        """
        Load data from a Parquet file.
        
        Args:
            filename: Name of the Parquet file
            
        Returns:
            DataFrame with loaded data
        """
        try:
            filepath = self.data_dir / filename
            df = pd.read_parquet(filepath)
            self.logger.info(f"Loaded {len(df)} rows from {filename}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading Parquet {filename}: {str(e)}")
            raise
    
    def save_parquet(self,
                    df: pd.DataFrame,
                    filename: str) -> None:
        """
        Save DataFrame to Parquet file.
        
        Args:
            df: DataFrame to save
            filename: Name of the output file
        """
        try:
            filepath = self.data_dir / filename
            df.to_parquet(filepath)
            self.logger.info(f"Saved {len(df)} rows to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving Parquet {filename}: {str(e)}")
            raise
    
    def list_files(self,
                  pattern: str = '*.csv') -> List[str]:
        """
        List data files matching a pattern.
        
        Args:
            pattern: File pattern to match
            
        Returns:
            List of matching filenames
        """
        try:
            files = glob.glob(str(self.data_dir / pattern))
            return [os.path.basename(f) for f in files]
        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            raise
    
    def get_file_info(self,
                     filename: str) -> Dict:
        """
        Get information about a data file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dictionary with file information
        """
        try:
            filepath = self.data_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"File {filename} not found")
            
            df = self.load_csv(filename) if filename.endswith('.csv') else self.load_parquet(filename)
            
            return {
                'rows': len(df),
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'file_size': filepath.stat().st_size
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {filename}: {str(e)}")
            raise
    
    def validate_data(self,
                     df: pd.DataFrame,
                     required_columns: List[str] = None) -> bool:
        """
        Validate DataFrame structure and content.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required columns
            
        Returns:
            True if data is valid
        """
        try:
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Check for NaN values
            if df.isnull().any().any():
                self.logger.warning("DataFrame contains NaN values")
            
            # Check for infinite values
            if np.isinf(df.select_dtypes(include=[np.number])).any().any():
                self.logger.warning("DataFrame contains infinite values")
            
            return True
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            return False
    
    def clean_data(self,
                  df: pd.DataFrame,
                  method: str = 'ffill') -> pd.DataFrame:
        """
        Clean DataFrame by handling missing values.
        
        Args:
            df: DataFrame to clean
            method: Method for handling missing values ('ffill', 'bfill', 'drop')
            
        Returns:
            Cleaned DataFrame
        """
        try:
            if method == 'ffill':
                df = df.ffill()
            elif method == 'bfill':
                df = df.bfill()
            elif method == 'drop':
                df = df.dropna()
            else:
                raise ValueError(f"Invalid method: {method}")
            
            self.logger.info(f"Cleaned data using method: {method}")
            return df
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            raise 
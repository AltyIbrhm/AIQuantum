import logging
import logging.config
import yaml
import os
from pathlib import Path

def setup_logging(config_path: str = None, default_level=logging.INFO):
    """
    Setup logging configuration
    """
    if config_path is not None and os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                # Create logs directory if it doesn't exist
                log_file = config.get('handlers', {}).get('file', {}).get('filename')
                if log_file:
                    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
                logging.config.dictConfig(config)
            except Exception as e:
                print(f'Error in logging configuration: {e}')
                setup_basic_logging(default_level)
    else:
        setup_basic_logging(default_level)

def setup_basic_logging(default_level=logging.INFO):
    """
    Setup basic logging configuration
    """
    logging.basicConfig(
        level=default_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/aiquantum.log')
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    """
    return logging.getLogger(name) 
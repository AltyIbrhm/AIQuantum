import pytest
import yaml
import os
from pathlib import Path
from AIQuantum.utils.config_loader import ConfigLoader

def test_config_loader_basic():
    """Test basic configuration loading."""
    # Create temporary config directory
    config_dir = Path("test_config")
    config_dir.mkdir(exist_ok=True)
    
    # Create test config file
    config_data = {
        'strategy': {
            'ema': {
                'short_window': 12,
                'long_window': 26
            },
            'macd': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            }
        },
        'risk': {
            'max_daily_drawdown': 0.05,
            'max_position_value': 10000
        }
    }
    
    config_path = config_dir / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    try:
        loader = ConfigLoader(str(config_dir))
        config = loader.load_config("config")
        
        # Check if config is loaded correctly
        assert 'strategy' in config
        assert 'risk' in config
        assert config['strategy']['ema']['short_window'] == 12
        assert config['risk']['max_daily_drawdown'] == 0.05
    finally:
        # Clean up
        if config_path.exists():
            config_path.unlink()
        if config_dir.exists():
            config_dir.rmdir()

def test_config_loader_validation():
    """Test configuration validation."""
    # Create temporary config directory
    config_dir = Path("test_config")
    config_dir.mkdir(exist_ok=True)
    
    # Create invalid config file
    invalid_config = {
        'strategy': {
            'ema': {
                'short_window': 'invalid',  # Should be int
                'long_window': 26
            }
        }
    }
    
    config_path = config_dir / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(invalid_config, f)
    
    try:
        loader = ConfigLoader(str(config_dir))
        with pytest.raises(Exception):  # Should raise when validating with schema
            _ = loader.get_base_config()
    finally:
        # Clean up
        if config_path.exists():
            config_path.unlink()
        if config_dir.exists():
            config_dir.rmdir()

def test_config_loader_edge_cases():
    """Test config loader with edge cases."""
    # Create temporary config directory
    config_dir = Path("test_config")
    config_dir.mkdir(exist_ok=True)
    
    empty_path = None
    invalid_path = None
    
    try:
        loader = ConfigLoader(str(config_dir))
        
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            loader.load_config("non_existent")
        
        # Test with empty file
        empty_path = config_dir / "empty_config.yaml"
        empty_path.touch()
        with pytest.raises(yaml.YAMLError):
            loader.load_config("empty_config")
        
        # Test with invalid YAML
        invalid_path = config_dir / "invalid_yaml.yaml"
        with open(invalid_path, 'w') as f:
            f.write('invalid: yaml: content')
        with pytest.raises(yaml.YAMLError):
            loader.load_config("invalid_yaml")
    finally:
        # Clean up
        if empty_path and empty_path.exists():
            empty_path.unlink()
        if invalid_path and invalid_path.exists():
            invalid_path.unlink()
        if config_dir.exists():
            config_dir.rmdir() 
import pytest
import yaml
import os
from AIQuantum.utils.config_loader import ConfigLoader

def test_config_loader_basic():
    """Test basic configuration loading."""
    # Create temporary config file
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
    
    with open('test_config.yaml', 'w') as f:
        yaml.dump(config_data, f)
    
    try:
        loader = ConfigLoader('test_config.yaml')
        config = loader.load()
        
        # Check if config is loaded correctly
        assert 'strategy' in config
        assert 'risk' in config
        assert config['strategy']['ema']['short_window'] == 12
        assert config['risk']['max_daily_drawdown'] == 0.05
    finally:
        # Clean up
        if os.path.exists('test_config.yaml'):
            os.remove('test_config.yaml')

def test_config_loader_validation():
    """Test configuration validation."""
    # Create invalid config file
    invalid_config = {
        'strategy': {
            'ema': {
                'short_window': 'invalid',  # Should be int
                'long_window': 26
            }
        }
    }
    
    with open('test_invalid_config.yaml', 'w') as f:
        yaml.dump(invalid_config, f)
    
    try:
        loader = ConfigLoader('test_invalid_config.yaml')
        with pytest.raises(ValueError):
            loader.load()
    finally:
        # Clean up
        if os.path.exists('test_invalid_config.yaml'):
            os.remove('test_invalid_config.yaml')

def test_config_loader_edge_cases():
    """Test config loader with edge cases."""
    # Test with non-existent file
    loader = ConfigLoader('non_existent.yaml')
    with pytest.raises(FileNotFoundError):
        loader.load()
    
    # Test with empty file
    with open('empty_config.yaml', 'w') as f:
        pass
    
    try:
        loader = ConfigLoader('empty_config.yaml')
        with pytest.raises(yaml.YAMLError):
            loader.load()
    finally:
        # Clean up
        if os.path.exists('empty_config.yaml'):
            os.remove('empty_config.yaml')
    
    # Test with invalid YAML
    with open('invalid_yaml.yaml', 'w') as f:
        f.write('invalid: yaml: content')
    
    try:
        loader = ConfigLoader('invalid_yaml.yaml')
        with pytest.raises(yaml.YAMLError):
            loader.load()
    finally:
        # Clean up
        if os.path.exists('invalid_yaml.yaml'):
            os.remove('invalid_yaml.yaml') 
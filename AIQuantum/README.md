# AIQuantum

AIQuantum is a sophisticated algorithmic trading system that combines traditional technical analysis with machine learning strategies for cryptocurrency trading.

## Project Structure

```
AIQuantum/
│
├── config/                 # Configuration files
│   ├── config.yaml        # Base configuration
│   ├── live_config.yaml   # Live trading settings
│   ├── risk_config.yaml   # Risk management settings
│   └── schema/            # Pydantic schemas for config validation
│
├── core/                  # Core components
│   ├── base_strategy.py
│   ├── base_risk_manager.py
│   └── base_trading_engine.py
│
├── data/                  # Data handling
│   ├── fetcher.py
│   ├── loader.py
│   └── preprocessing.py
│
├── models/                # ML models
│   ├── lstm_model.py
│   ├── model_utils.py
│   └── saved/            # Trained models
│
├── strategy/              # Trading strategies
│   ├── technical/        # Technical analysis
│   └── ml/              # Machine learning
│
├── risk/                  # Risk management
│   ├── risk_engine.py
│   ├── constraints.py
│   └── sizing.py
│
├── trading/               # Trading execution
│   ├── live_trading_engine.py
│   └── paper_trading_engine.py
│
├── dashboard/             # Monitoring and visualization
│   ├── rich_dashboard.py
│   └── performance_plotter.py
│
├── utils/                 # Utilities
│   ├── config_loader.py
│   ├── logger.py
│   └── helpers.py
│
├── tests/                 # Test suite
│
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Features

- Multiple trading strategies (Technical + ML)
- Comprehensive risk management
- Paper and live trading modes
- Real-time monitoring dashboard
- Configurable through YAML files
- Extensive logging and error handling

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIQuantum.git
cd AIQuantum
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your settings:
- Copy `config/config.yaml.example` to `config/config.yaml`
- Adjust settings in the configuration files
- For live trading, set up your API keys in `config/live_config.yaml`

5. Run the system:
```bash
python main.py
```

## Configuration

The system uses multiple YAML configuration files:

- `config.yaml`: Base configuration
- `live_config.yaml`: Live trading settings
- `risk_config.yaml`: Risk management parameters

All configurations are validated using Pydantic schemas in the `config/schema` directory.

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Strategies
1. Create a new strategy class in `strategy/technical/` or `strategy/ml/`
2. Implement the required interface from `core/base_strategy.py`
3. Add configuration schema in `config/schema/strategy_schema.py`
4. Update `config.yaml` to include the new strategy

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
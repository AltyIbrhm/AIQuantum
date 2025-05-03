# AIQuantum Trading System

A sophisticated algorithmic trading system that combines technical analysis and machine learning for cryptocurrency trading on BinanceUS.

## Features

- Real-time and historical data fetching from BinanceUS
- Technical analysis indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- Machine learning models for price prediction
- Risk management and position sizing
- Paper and live trading support
- Comprehensive logging and monitoring

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AltyIbrhm/AIQuantum.git
cd AIQuantum
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```bash
# BinanceUS API Credentials
BINANCEUS_API_KEY=your_api_key_here
BINANCEUS_API_SECRET=your_api_secret_here

# Trading Configuration
TRADING_MODE=paper  # paper or live
PAPER_BALANCE=10000.0

# Data Configuration
DATA_DIR=data/
CACHE_DIR=data/cache/
CACHE_EXPIRATION=3600

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/aiquantum.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Monitoring Configuration
MONITORING_ENABLED=true
MONITORING_INTERVAL=300
ALERT_EMAIL=your_email@example.com
SLACK_WEBHOOK=your_slack_webhook_url

# Risk Management
MAX_DRAWDOWN=0.2
STOP_LOSS=0.05
TAKE_PROFIT=0.1
MAX_POSITION_SIZE=0.2
RISK_PER_TRADE=0.02

# Technical Analysis
DEFAULT_TIMEFRAME=1h
DEFAULT_SYMBOL=BTC/USDT

# Machine Learning
SEQUENCE_LENGTH=60
TRAIN_TEST_SPLIT=0.8
VALIDATION_SPLIT=0.1
BATCH_SIZE=32
EPOCHS=100
```

## Configuration

The system is configured through `config/config.yaml`. Key configurations include:

- Exchange settings (BinanceUS specific)
- Trading parameters
- Risk management rules
- Technical analysis indicators
- Machine learning parameters
- Logging and monitoring settings

## Usage

1. Start the trading system:
```bash
python main.py
```

2. For paper trading:
```bash
python main.py --mode paper
```

3. For live trading:
```bash
python main.py --mode live
```

## Project Structure

```
AIQuantum/
├── config/             # Configuration files
├── data/              # Data processing modules
│   ├── fetcher.py     # Data fetching from BinanceUS
│   ├── loader.py      # Local data management
│   └── preprocessing.py # Data preprocessing
├── core/              # Core trading components
├── strategy/          # Trading strategies
├── risk/              # Risk management
├── models/            # Machine learning models
├── utils/             # Utility functions
└── tests/             # Test suite
```

## BinanceUS Integration

The system is specifically configured for BinanceUS, with features including:

- US-specific trading pairs
- Compliance with US regulations
- Spot trading only (no margin/leverage)
- Rate limiting and timeout settings
- Market validation and error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. 
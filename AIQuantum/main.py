import os
from pathlib import Path
from utils.logger import setup_logging, get_logger
from utils.config_loader import ConfigLoader, load_config
from data.mock_data import get_mock_ohlcv_data
from data.preprocessing import preprocess_data
from strategy.signal_combiner import SignalCombiner
from risk.risk_engine import RiskEngine
import pandas as pd

def main():
    # 1. Load config
    config = load_config("config/config.yaml")
    logger = setup_logger(config.logging.level)

    logger.info("🚀 AIQuantum Simulation Started")

    # 2. Load or fetch data
    df = get_mock_ohlcv_data(
        symbol=config.exchange.symbol,
        timeframe=config.exchange.timeframe,
        days=30,
        config=config
    )

    if df.empty:
        logger.error("❌ No OHLCV data available. Exiting.")
        return

    logger.info(f"📊 Loaded {len(df)} candles of OHLCV data")

    # 3. Preprocess data
    processed_df = preprocess_data(df)
    logger.info("✅ Data preprocessing completed")

    # 4. Initialize signal combiner
    signal_combiner = SignalCombiner(config.strategy)
    logger.info("✅ Signal combiner initialized")

    # 5. Generate signal
    signal_payload = signal_combiner.generate_signal(processed_df)
    logger.info(f"📊 Signal: {signal_payload['signal']} | Confidence: {signal_payload['confidence']:.2f}")

    # 6. Initialize risk engine
    risk_engine = RiskEngine(config.risk)
    logger.info("✅ Risk engine initialized")

    # 7. Evaluate risk and sizing
    risk_result = risk_engine.evaluate_trade(
        decision=signal_payload['signal'],
        confidence=signal_payload['confidence'],
        volatility=signal_payload.get('volatility', 0.02),
        trend_alignment=signal_payload.get('trend_alignment', 0.0),
        current_price=processed_df['close'].iloc[-1],
        portfolio_value=10000.0  # Mock portfolio value
    )

    if risk_result["approved"]:
        logger.info(f"✅ TRADE APPROVED: {risk_result['action']} with position size {risk_result['size']:.4f}")
        logger.info(f"📊 Risk Metrics: Drawdown {risk_result['metadata']['daily_drawdown']:.2%} | Open Trades: {risk_result['metadata']['open_trades']}")
    else:
        logger.info(f"🚫 TRADE REJECTED: Reason - {risk_result['reason']}")

    # 8. Print final state
    logger.info("📊 Final State:")
    logger.info(f"  - Portfolio Value: $10,000.00")
    logger.info(f"  - Daily Drawdown: {risk_engine.get_state()['daily_drawdown']:.2%}")
    logger.info(f"  - Open Trades: {risk_engine.get_state()['open_trades']}")
    logger.info(f"  - Last Trade Time: {risk_engine.get_state()['last_trade_time']}")

if __name__ == "__main__":
    main() 
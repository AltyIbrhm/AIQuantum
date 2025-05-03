import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from .technical.ema import EMAStrategy
from .technical.macd import MACDStrategy
from .technical.bollinger import BollingerStrategy
from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

class SignalCombiner:
    """
    Signal combiner implementation.
    Aggregates signals from multiple strategies with weighted scoring and confidence thresholds.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize signal combiner with configuration.
        
        Args:
            config: Combiner configuration dictionary
        """
        self.logger = get_logger(__name__)
        
        # Default configuration
        self.config = {
            'strategies': {
                'ema': {
                    'enabled': True,
                    'weight': 0.3,
                    'min_confidence': 0.6
                },
                'macd': {
                    'enabled': True,
                    'weight': 0.4,
                    'min_confidence': 0.7
                },
                'bollinger': {
                    'enabled': True,
                    'weight': 0.3,
                    'min_confidence': 0.6
                }
            },
            'min_combined_confidence': 0.7,
            'debug': False
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Initialize strategies
        self.strategies: Dict[str, BaseStrategy] = {}
        self._initialize_strategies()
        
        self.logger.info(f"Initialized signal combiner with config: {self.config}")
    
    def _initialize_strategies(self) -> None:
        """
        Initialize all enabled strategies.
        """
        try:
            if self.config['strategies']['ema']['enabled']:
                self.strategies['ema'] = EMAStrategy()
            
            if self.config['strategies']['macd']['enabled']:
                self.strategies['macd'] = MACDStrategy()
            
            if self.config['strategies']['bollinger']['enabled']:
                self.strategies['bollinger'] = BollingerStrategy()
            
            self.logger.info(f"Initialized {len(self.strategies)} strategies")
        except Exception as e:
            self.logger.error(f"Error initializing strategies: {str(e)}")
            raise
    
    def calculate_signals(self, data: pd.DataFrame) -> Dict:
        """
        Calculate combined signals from all enabled strategies.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with combined signals and metadata
        """
        try:
            # Initialize results
            results = {
                'signals': {},
                'combined_signal': 0,
                'combined_confidence': 0.0,
                'strategy_weights': {},
                'strategy_confidences': {},
                'debug_info': {}
            }
            
            # Calculate signals for each strategy
            for name, strategy in self.strategies.items():
                try:
                    # Get strategy config
                    strategy_config = self.config['strategies'][name]
                    
                    # Calculate signals
                    signals = strategy.calculate_signals(data)
                    
                    # Extract relevant information
                    last_signal = signals['signal'].iloc[-1]
                    last_strength = signals['strength'].iloc[-1]
                    
                    # Calculate confidence
                    confidence = self._calculate_confidence(signals, strategy_config)
                    
                    # Store results
                    results['signals'][name] = {
                        'signal': last_signal,
                        'strength': last_strength,
                        'confidence': confidence,
                        'raw_data': signals
                    }
                    
                    # Store weights and confidences
                    results['strategy_weights'][name] = strategy_config['weight']
                    results['strategy_confidences'][name] = confidence
                    
                    # Store debug info if enabled
                    if self.config['debug']:
                        results['debug_info'][name] = {
                            'last_signal': last_signal,
                            'last_strength': last_strength,
                            'confidence': confidence,
                            'trend': signals['trend_ema'].iloc[-1] if 'trend_ema' in signals else None,
                            'volatility': signals['volatility'].iloc[-1] if 'volatility' in signals else None
                        }
                    
                except Exception as e:
                    self.logger.error(f"Error calculating signals for {name}: {str(e)}")
                    continue
            
            # Calculate combined signal and confidence
            combined_signal, combined_confidence = self._combine_signals(results)
            
            # Update results
            results['combined_signal'] = combined_signal
            results['combined_confidence'] = combined_confidence
            
            # Add decision
            results['decision'] = self._make_decision(combined_signal, combined_confidence)
            
            self.logger.info(f"Generated combined signal: {results['decision']} with confidence: {combined_confidence:.2f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating combined signals: {str(e)}")
            raise
    
    def _calculate_confidence(self, signals: pd.DataFrame, strategy_config: Dict) -> float:
        """
        Calculate confidence score for a strategy's signals.
        
        Args:
            signals: DataFrame with strategy signals
            strategy_config: Strategy configuration
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Get last signal and strength
            last_signal = signals['signal'].iloc[-1]
            last_strength = signals['strength'].iloc[-1]
            
            # Base confidence on signal strength
            confidence = last_strength
            
            # Adjust confidence based on trend alignment
            if 'trend_ema' in signals:
                trend = signals['trend_ema'].iloc[-1]
                price = signals.index[-1]
                if (last_signal > 0 and price > trend) or (last_signal < 0 and price < trend):
                    confidence *= 1.2  # Boost confidence for trend-aligned signals
            
            # Adjust confidence based on volatility
            if 'volatility' in signals:
                volatility = signals['volatility'].iloc[-1]
                confidence *= (1 + volatility)  # Higher volatility = higher confidence
            
            # Ensure confidence is within bounds
            confidence = max(0.0, min(1.0, confidence))
            
            return confidence
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0
    
    def _combine_signals(self, results: Dict) -> Tuple[int, float]:
        """
        Combine signals from all strategies with weighted scoring.
        
        Args:
            results: Dictionary with strategy signals and metadata
            
        Returns:
            Tuple of (combined signal, combined confidence)
        """
        try:
            weighted_signal = 0.0
            total_weight = 0.0
            weighted_confidence = 0.0
            
            for name, data in results['signals'].items():
                # Get strategy config
                strategy_config = self.config['strategies'][name]
                
                # Skip if confidence below threshold
                if data['confidence'] < strategy_config['min_confidence']:
                    continue
                
                # Calculate weighted signal
                weight = strategy_config['weight']
                weighted_signal += data['signal'] * weight * data['confidence']
                weighted_confidence += weight * data['confidence']
                total_weight += weight
            
            # Normalize if we have weights
            if total_weight > 0:
                weighted_signal /= total_weight
                weighted_confidence /= total_weight
            
            # Convert to integer signal
            combined_signal = int(np.sign(weighted_signal))
            
            return combined_signal, weighted_confidence
        except Exception as e:
            self.logger.error(f"Error combining signals: {str(e)}")
            return 0, 0.0
    
    def _make_decision(self, signal: int, confidence: float) -> str:
        """
        Make final trading decision based on combined signal and confidence.
        
        Args:
            signal: Combined signal (-1, 0, 1)
            confidence: Combined confidence score
            
        Returns:
            Trading decision ('BUY', 'SELL', 'HOLD')
        """
        try:
            # Check minimum confidence threshold
            if confidence < self.config['min_combined_confidence']:
                return 'HOLD'
            
            # Make decision based on signal
            if signal > 0:
                return 'BUY'
            elif signal < 0:
                return 'SELL'
            else:
                return 'HOLD'
        except Exception as e:
            self.logger.error(f"Error making decision: {str(e)}")
            return 'HOLD'
    
    def get_metadata(self) -> Dict:
        """
        Get combiner metadata.
        
        Returns:
            Dictionary with combiner metadata
        """
        return {
            'name': 'Signal Combiner',
            'version': '1.0.0',
            'parameters': self.config,
            'description': 'Combines signals from multiple strategies with weighted scoring and confidence thresholds',
            'active_strategies': list(self.strategies.keys())
        } 
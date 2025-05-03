from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from ...utils.logger import get_logger

class ConfidenceEngine:
    """Engine for evaluating signal confidence based on multiple factors."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the confidence engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Confidence weights for different factors
        self.weights = {
            'trend_alignment': config.get('trend_weight', 0.3),
            'volatility': config.get('volatility_weight', 0.2),
            'signal_strength': config.get('signal_weight', 0.3),
            'volume': config.get('volume_weight', 0.2)
        }
        
        # Normalize weights to sum to 1
        weight_sum = sum(self.weights.values())
        self.weights = {k: v/weight_sum for k, v in self.weights.items()}
        
        # Thresholds
        self.min_confidence = config.get('min_confidence', 0.3)
        self.high_volatility_threshold = config.get('high_volatility_threshold', 0.02)
        self.volume_baseline = config.get('volume_baseline', 1000000)
    
    def calculate_confidence(
        self,
        signal_strength: float,
        trend_alignment: float,
        volatility: float,
        volume: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate overall confidence score for a trading signal.
        
        Args:
            signal_strength: Strength of the trading signal (-1 to 1)
            trend_alignment: Alignment with overall trend (-1 to 1)
            volatility: Current market volatility
            volume: Trading volume
            metadata: Additional metadata for confidence calculation
            
        Returns:
            Dictionary containing confidence score and factor contributions
        """
        try:
            # Normalize inputs
            signal_conf = abs(signal_strength)
            trend_conf = abs(trend_alignment)
            vol_conf = self._calculate_volatility_confidence(volatility)
            volume_conf = self._calculate_volume_confidence(volume)
            
            # Calculate weighted confidence
            confidence_factors = {
                'signal_strength': signal_conf,
                'trend_alignment': trend_conf,
                'volatility': vol_conf,
                'volume': volume_conf
            }
            
            # Calculate total confidence
            total_confidence = sum(
                self.weights[factor] * score
                for factor, score in confidence_factors.items()
            )
            
            # Apply minimum threshold
            final_confidence = max(total_confidence, self.min_confidence)
            
            return {
                'confidence': final_confidence,
                'factors': confidence_factors,
                'weights': self.weights,
                'metadata': metadata or {}
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return {
                'confidence': self.min_confidence,
                'factors': {},
                'weights': self.weights,
                'error': str(e)
            }
    
    def _calculate_volatility_confidence(self, volatility: float) -> float:
        """Calculate confidence factor based on volatility.
        
        Args:
            volatility: Market volatility value
            
        Returns:
            Confidence score (0 to 1)
        """
        try:
            # Higher volatility = lower confidence
            if volatility > self.high_volatility_threshold:
                return 0.5 * (self.high_volatility_threshold / volatility)
            return 1.0 - (volatility / self.high_volatility_threshold) * 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility confidence: {str(e)}")
            return 0.5
    
    def _calculate_volume_confidence(self, volume: float) -> float:
        """Calculate confidence factor based on volume.
        
        Args:
            volume: Trading volume
            
        Returns:
            Confidence score (0 to 1)
        """
        try:
            # Higher volume = higher confidence
            return min(1.0, volume / self.volume_baseline)
            
        except Exception as e:
            self.logger.error(f"Error calculating volume confidence: {str(e)}")
            return 0.5
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the confidence engine.
        
        Returns:
            Dictionary containing engine metadata
        """
        return {
            'weights': self.weights,
            'thresholds': {
                'min_confidence': self.min_confidence,
                'high_volatility': self.high_volatility_threshold,
                'volume_baseline': self.volume_baseline
            },
            'config': self.config
        } 
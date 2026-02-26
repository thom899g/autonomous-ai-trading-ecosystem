"""
Configuration management for the trading ecosystem.
Centralizes all config with environment variable support.
"""
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import firebase_admin
from firebase_admin import credentials, firestore
import logging

class TradingMode(Enum):
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"

@dataclass
class ExchangeConfig:
    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    rate_limit: int = 1000
    enable_rate_limit: bool = True

@dataclass
class ModelConfig:
    retrain_interval_hours: int = 24
    min_training_samples: int = 1000
    feature_window_size: int = 50
    validation_split: float = 0.2

class TradingConfig:
    def __init__(self):
        self.mode = TradingMode(os.getenv("TRADING_MODE", "paper"))
        self.initial_capital = float(os.getenv("INITIAL_CAPITAL", 10000.0))
        self.max_position_size_pct = float(os.getenv("MAX_POSITION_PCT", 0.1))
        self.stop_loss_pct = float(os.getenv("STOP_LOSS_PCT", 0.02))
        self.take_profit_pct = float(os.getenv("TAKE_PROFIT_PCT", 0.05))
        
        # Exchange configurations
        self.exchanges: Dict[str, ExchangeConfig] = self._load_exchange_configs()
        
        # Model configurations
        self.model_config = ModelConfig()
        
        # Risk management
        self.max_daily_loss_pct = 0.05
        self.max_concurrent_trades = 5
        
        # Initialize Firebase if credentials exist
        self.firestore_client = self._init_firebase()
    
    def _load_exchange_configs(self) -> Dict[str, ExchangeConfig]:
        """Load exchange configurations from environment variables."""
        exchanges = {}
        exchange_list = os.getenv("ENABLED_EXCHANGES", "binance,coinbase").split(",")
        
        for exchange in exchange_list:
            exchanges[exchange] = ExchangeConfig(
                name=exchange,
                api_key=os.getenv(f"{exchange.upper()}_API_KEY"),
                api_secret=os.getenv(f"{exchange.upper()}_API_SECRET")
            )
        
        return exchanges
    
    def _init_firebase(self):
        """Initialize Firebase Firestore client."""
        try:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            else:
                logging.warning("Firebase credentials not found. Using local state only.")
                return None
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for logging/persistence."""
        return {
            "mode": self.mode.value,
            "initial_capital": self.initial_capital,
            "max_position_size_pct": self.max_position_size_pct,
            "exchanges": [ex.name for ex in self.exchanges.values()],
            "model_retrain_interval": self.model_config.retrain_interval_hours
        }

# Global configuration instance
CONFIG = TradingConfig()
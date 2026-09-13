"""
Advanced Sportybet Bot with Configuration Management
Extends the basic bot with config file loading, extra features, and monitoring
"""

import asyncio
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

from sportybet_bot import SportybetBot, PredictionDatabase, AntiDetectionModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Load and manage bot configuration"""
    
    def __init__(self, config_path: str = "Scripts/sportybet_config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.info("Creating default config...")
            self.create_default_config()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"✅ Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config = {
            'sportybet': {
                'username': 'your_username_here',
                'password': 'your_password_here',
                'headless': False
            },
            'betting': {
                'stake_per_bet': 10.0,
                'min_odds': 1.5,
                'max_odds': 100.0,
                'auto_select': {'enable': True, 'selection_threshold': 0.65}
            },
            'database': {
                'predictions_dir': 'Datasets/Predictions',
                'filter_by_confidence': True,
                'min_confidence': 0.60
            }
        }
        logger.info("Default configuration created")
    
    def get(self, key: str, default=None):
        """Get config value with dot notation (e.g., 'sportybet.username')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value


class AdvancedSportybetBot(SportybetBot):
    """Extended bot with config management and advanced features"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        
        username = config.get('sportybet.username')
        password = config.get('sportybet.password')
        headless = config.get('sportybet.headless', False)
        
        super().__init__(username, password, headless)
        
        self.stake = config.get('betting.stake_per_bet', 10.0)
        self.min_odds = config.get('betting.min_odds', 1.5)
        self.max_odds = config.get('betting.max_odds', 100.0)
        self.min_confidence = config.get('database.min_confidence', 0.60)
        self.max_bets_per_day = config.get('safety.max_bets_per_day', 50)
        self.dry_run = config.get('safety.dry_run', False)
        
        self.bets_placed = 0
        self.start_time = None
    
    async def filter_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Filter predictions based on configuration"""
        logger.info(f"Filtering {len(predictions)} predictions...")
        
        filtered = []
        for pred in predictions:
            # Check confidence threshold
            confidence = pred.get('confidence', pred.get('probability', 0))
            if confidence < self.min_confidence:
                logger.debug(f"Skipping {pred.get('home')} vs {pred.get('away')} - Low confidence: {confidence}")
                continue
            
            # Check odds
            odds = pred.get('odds', 0)
            if odds < self.min_odds or odds > self.max_odds:
                logger.debug(f"Skipping {pred.get('home')} vs {pred.get('away')} - Odds {odds} out of range")
                continue
            
            filtered.append(pred)
        
        logger.info(f"✅ {len(filtered)} predictions passed filters")
        return filtered
    
    async def log_betting_session(self, predictions: List[Dict], added_count: int):
        """Log betting session details"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'total_predictions': len(predictions),
            'bets_added': added_count,
            'session_duration': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'predictions': [
                {
                    'home': p.get('home'),
                    'away': p.get('away'),
                    'prediction': p.get('prediction'),
                    'odds': p.get('odds'),
                    'confidence': p.get('confidence', p.get('probability'))
                }
                for p in predictions
            ]
        }
        
        # Save to JSON log
        log_dir = Path('logs/sessions')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import json
            with open(session_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            logger.info(f"✅ Session logged to {session_file}")
        except Exception as e:
            logger.error(f"Error logging session: {e}")
    
    async def run(self, predictions: Optional[List[Dict]] = None, csv_path: Optional[str] = None):
        """Run with advanced features"""
        self.start_time = datetime.now()
        
        try:
            logger.info("\n" + "="*60)
            logger.info("🤖 SPORTYBET AUTOMATED BETTING BOT")
            logger.info("="*60)
            logger.info(f"Start Time: {self.start_time}")
            logger.info(f"Dry Run: {self.dry_run}")
            logger.info("="*60 + "\n")
            
            await self.launch_browser()
            
            # Load predictions
            if predictions is None:
                csv_path = csv_path or self.config.get('database.csv_path')
                if csv_path:
                    predictions = self.prediction_db.load_csv_predictions(csv_path)
                else:
                    predictions = self.prediction_db.load_today_predictions()
            
            if not predictions:
                logger.warning("⚠️  No predictions found")
                return
            
            # Filter predictions
            predictions = await self.filter_predictions(predictions)
            
            if not predictions:
                logger.warning("⚠️  No predictions passed filters")
                return
            
            # Login
            if not await self.login_sportybet():
                logger.error("❌ Failed to login")
                return
            
            # Navigate to today's games
            if not await self.navigate_to_today_games():
                logger.error("❌ Failed to navigate to today's games")
                return
            
            # Process predictions
            added = await self.process_predictions(predictions)
            
            # Log session
            await self.log_betting_session(predictions, added)
            
            # Pause for review unless dry run
            if added > 0 and not self.dry_run:
                await self.pause_for_review()
            elif self.dry_run:
                logger.info("🔍 DRY RUN MODE - No actual bets placed")
        
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.close_browser()


async def main():
    """Main entry point with config"""
    
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('logs/screenshots').mkdir(exist_ok=True)
    Path('logs/sessions').mkdir(exist_ok=True)
    
    # Load configuration
    config = ConfigManager()
    
    # Initialize bot
    bot = AdvancedSportybetBot(config)
    
    # Run bot
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())

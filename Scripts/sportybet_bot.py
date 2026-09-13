"""
Sportybet.gh Automated Betting Bot
Intelligent bot that loads ScoreCast predictions to Sportybet slip
Features:
- Advanced anti-detection evasion (realistic delays, mouse movements, user agents)
- Loads predictions for today's games from ScoreCast database
- Matches fixtures with Sportybet markets
- Fills betting slip automatically
- Pauses for manual review before submission
"""

import asyncio
import random
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import time

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sportybet_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AntiDetectionModule:
    """Handle all anti-bot detection evasion techniques"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Return random user agent"""
        return random.choice(AntiDetectionModule.USER_AGENTS)
    
    @staticmethod
    async def human_delay(min_sec: float = 0.5, max_sec: float = 3.0):
        """Simulate human reaction time with randomness"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def scroll_page(page: Page):
        """Simulate human scrolling behavior"""
        await page.evaluate('''
            window.scrollBy(0, window.innerHeight);
        ''')
        await AntiDetectionModule.human_delay(0.3, 0.8)
    
    @staticmethod
    async def random_mouse_movement(page: Page):
        """Simulate random mouse movements"""
        # Get random position on viewport
        x = random.randint(100, 1200)
        y = random.randint(100, 800)
        await page.mouse.move(x, y)
        await AntiDetectionModule.human_delay(0.2, 0.5)


class PredictionDatabase:
    """Load and manage ScoreCast predictions"""
    
    def __init__(self, predictions_dir: str = "Datasets/Predictions"):
        self.predictions_dir = Path(predictions_dir)
        self.predictions = []
    
    def load_today_predictions(self) -> List[Dict]:
        """Load predictions for today's games"""
        logger.info("Loading today's predictions from ScoreCast...")
        
        today = datetime.now().date()
        predictions = []
        
        # Look for prediction files
        if not self.predictions_dir.exists():
            logger.warning(f"Predictions directory not found: {self.predictions_dir}")
            return []
        
        for pred_file in self.predictions_dir.glob("*.json"):
            try:
                with open(pred_file, 'r') as f:
                    data = json.load(f)
                    
                    # Filter for today's games
                    if isinstance(data, list):
                        for fixture in data:
                            if 'date' in fixture:
                                fixture_date = datetime.fromisoformat(fixture['date']).date()
                                if fixture_date == today:
                                    predictions.append(fixture)
                    elif isinstance(data, dict) and 'fixtures' in data:
                        for fixture in data['fixtures']:
                            if 'date' in fixture:
                                fixture_date = datetime.fromisoformat(fixture['date']).date()
                                if fixture_date == today:
                                    predictions.append(fixture)
            except Exception as e:
                logger.error(f"Error loading predictions from {pred_file}: {e}")
        
        logger.info(f"Found {len(predictions)} predictions for today")
        return predictions
    
    def load_csv_predictions(self, csv_path: str) -> List[Dict]:
        """Load predictions from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            today = datetime.now().date()
            
            # Filter for today
            df['date'] = pd.to_datetime(df['date']).dt.date
            today_df = df[df['date'] == today]
            
            predictions = today_df.to_dict('records')
            logger.info(f"Loaded {len(predictions)} predictions from CSV")
            return predictions
        except Exception as e:
            logger.error(f"Error loading CSV predictions: {e}")
            return []


class SportybetBot:
    """Main Sportybet automation bot"""
    
    def __init__(self, username: str, password: str, headless: bool = False):
        self.username = username
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.prediction_db = PredictionDatabase()
        self.anti_detection = AntiDetectionModule()
    
    async def launch_browser(self):
        """Launch Playwright browser with anti-detection"""
        logger.info("Launching browser with anti-detection measures...")
        
        playwright = await async_playwright().start()
        
        # Launch browser with stealth options
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            user_agent=self.anti_detection.get_random_user_agent(),
            viewport={'width': 1280, 'height': 720},
            locale='en-GH',
            timezone_id='Africa/Accra',
            permissions=['geolocation'],
            geolocation={'latitude': 5.6037, 'longitude': -0.1870},  # Accra, Ghana
        )
        
        # Add stealth script
        await self.context.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        ''')
        
        self.page = await self.context.new_page()
        logger.info("Browser launched successfully")
    
    async def login_sportybet(self) -> bool:
        """Login to Sportybet account"""
        logger.info("Attempting to login to Sportybet...")
        
        try:
            # Navigate to Sportybet
            await self.page.goto('https://www.sportybet.com', wait_until='networkidle')
            await self.anti_detection.human_delay(2, 4)
            
            # Click login button
            logger.info("Clicking login button...")
            await self.page.click('[data-testid="login-button"], .login-btn, button:has-text("Login"), a:has-text("Login")')
            await self.anti_detection.human_delay(1, 2)
            
            # Fill username
            logger.info("Entering username...")
            await self.page.fill('input[name="username"], input[type="email"], input[type="text"]', self.username)
            await self.anti_detection.human_delay(0.5, 1)
            
            # Fill password
            logger.info("Entering password...")
            await self.page.fill('input[name="password"], input[type="password"]', self.password)
            await self.anti_detection.human_delay(0.5, 1)
            
            # Random mouse movement before submit
            await self.anti_detection.random_mouse_movement(self.page)
            
            # Submit login
            logger.info("Submitting login form...")
            await self.page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")')
            
            # Wait for dashboard/betslip area
            await asyncio.sleep(3)
            
            # Verify login success
            is_logged_in = await self.page.query_selector('[data-testid="betslip"], .betslip, .slip') is not None
            
            if is_logged_in:
                logger.info("✅ Successfully logged into Sportybet")
                return True
            else:
                logger.warning("⚠️ Login may have failed - betslip area not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    async def navigate_to_today_games(self) -> bool:
        """Navigate to today's games section"""
        logger.info("Navigating to today's games...")
        
        try:
            # Different selectors to try for today's games
            selectors = [
                '[data-testid="today"], [class*="today"], a:has-text("Today")',
                '.today-games, .games-today',
                'button:has-text("Today")',
            ]
            
            for selector in selectors:
                element = await self.page.query_selector(selector)
                if element:
                    await element.click()
                    await self.anti_detection.human_delay(2, 3)
                    logger.info("✅ Navigated to today's games")
                    return True
            
            logger.warning("Could not find 'Today' section, trying home page")
            await self.page.goto('https://www.sportybet.com/sports/football', wait_until='networkidle')
            await self.anti_detection.human_delay(2, 3)
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to today's games: {e}")
            return False
    
    async def find_fixture_on_sportybet(self, prediction: Dict) -> bool:
        """Find and click a specific fixture on Sportybet"""
        logger.info(f"Looking for fixture: {prediction.get('home')} vs {prediction.get('away')}")
        
        try:
            # Extract team names
            home_team = prediction.get('home', '').strip()
            away_team = prediction.get('away', '').strip()
            
            if not home_team or not away_team:
                logger.warning(f"Invalid prediction data: {prediction}")
                return False
            
            logger.info(f"Searching for: {home_team} vs {away_team}")
            
            # Look for fixture element
            fixtures = await self.page.query_selector_all('[data-testid*="fixture"], .fixture, .match-item, .game')
            
            for fixture in fixtures:
                text = await fixture.text_content()
                if home_team.lower() in text.lower() and away_team.lower() in text.lower():
                    logger.info(f"✅ Found fixture on Sportybet")
                    await fixture.click()
                    await self.anti_detection.human_delay(1, 2)
                    return True
            
            logger.warning(f"Could not find {home_team} vs {away_team} on Sportybet")
            return False
            
        except Exception as e:
            logger.error(f"Error finding fixture: {e}")
            return False
    
    async def select_market_and_odds(self, prediction: Dict) -> bool:
        """Select market and odds from prediction"""
        logger.info(f"Selecting market and odds for prediction...")
        
        try:
            market_type = prediction.get('market_type', '1X2')
            prediction_value = prediction.get('prediction', prediction.get('pick'))
            odds = prediction.get('odds', 0)
            
            logger.info(f"Market: {market_type}, Pick: {prediction_value}, Odds: {odds}")
            
            # Find and click the odds button
            odds_selectors = [
                f'button:has-text("{odds}")',
                f'[data-odds="{odds}"]',
                f'[data-testid*="odds"]',
                '.odds-button',
            ]
            
            for selector in odds_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        await element.click()
                        await self.anti_detection.human_delay(0.5, 1)
                        logger.info(f"✅ Selected odds: {odds}")
                        return True
                except:
                    continue
            
            logger.info(f"Trying to select {prediction_value}...")
            
            prediction_selectors = [
                f'button:has-text("{prediction_value}")',
                f'[data-pick="{prediction_value}"]',
                f'[title="{prediction_value}"]',
            ]
            
            for selector in prediction_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        await element.click()
                        await self.anti_detection.human_delay(0.5, 1)
                        logger.info(f"✅ Selected prediction: {prediction_value}")
                        return True
                except:
                    continue
            
            logger.warning("Could not select market/odds - will need manual selection")
            return False
            
        except Exception as e:
            logger.error(f"Error selecting market: {e}")
            return False
    
    async def add_to_betslip(self) -> bool:
        """Add selection to betslip"""
        logger.info("Adding selection to betslip...")
        
        try:
            # Try various selectors for add to slip button
            add_selectors = [
                'button:has-text("Add to Slip")',
                'button:has-text("Add to Betslip")',
                '[data-testid="add-to-slip"]',
                '.add-to-slip-btn',
                'button:has-text("Add")',
            ]
            
            for selector in add_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        await element.click()
                        await self.anti_detection.human_delay(1, 2)
                        logger.info("✅ Added to betslip")
                        return True
                except:
                    continue
            
            logger.warning("Could not find 'Add to Slip' button")
            return False
            
        except Exception as e:
            logger.error(f"Error adding to betslip: {e}")
            return False
    
    async def process_predictions(self, predictions: List[Dict]) -> int:
        """Process all predictions and add to betslip"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {len(predictions)} predictions")
        logger.info(f"{'='*60}\n")
        
        added_count = 0
        
        for i, prediction in enumerate(predictions, 1):
            logger.info(f"\n[{i}/{len(predictions)}] Processing prediction...")
            logger.info(f"Details: {prediction}")
            
            try:
                # Navigate back to today's games for next fixture
                if i > 1:
                    await self.navigate_to_today_games()
                    await self.anti_detection.human_delay(1, 2)
                
                # Find fixture
                if not await self.find_fixture_on_sportybet(prediction):
                    logger.warning(f"Skipping prediction {i}")
                    continue
                
                # Select market and odds
                if not await self.select_market_and_odds(prediction):
                    logger.warning(f"Could not select market for prediction {i}")
                
                # Add to betslip
                if await self.add_to_betslip():
                    added_count += 1
                    logger.info(f"✅ Successfully added prediction {i} to betslip")
                else:
                    logger.warning(f"Failed to add prediction {i} to betslip")
                
                # Random delay between predictions to avoid detection
                await self.anti_detection.human_delay(2, 4)
                
            except Exception as e:
                logger.error(f"Error processing prediction {i}: {e}")
                continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Successfully added {added_count} predictions to betslip")
        logger.info(f"{'='*60}\n")
        
        return added_count
    
    async def pause_for_review(self):
        """Pause and keep browser open for manual review"""
        logger.info("\n" + "="*60)
        logger.info("⏸️  PAUSED FOR MANUAL REVIEW")
        logger.info("="*60)
        logger.info("\n✅ All predictions have been loaded to your betslip")
        logger.info("📋 Please review the slip and make final adjustments")
        logger.info("💰 Stake: Verify your stake amount")
        logger.info("✔️  Confirm and place bet manually when ready")
        logger.info("\n🔴 Browser will remain open. Close VSCode terminal to exit.\n")
        logger.info("="*60 + "\n")
        
        # Wait for user to close the script
        try:
            await self.page.pause()
        except:
            # If pause not available, just wait indefinitely
            await asyncio.sleep(999999)
    
    async def close_browser(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser closed")
    
    async def run(self, predictions: Optional[List[Dict]] = None, csv_path: Optional[str] = None):
        """Main execution flow"""
        try:
            await self.launch_browser()
            
            # Load predictions
            if predictions is None:
                if csv_path:
                    predictions = self.prediction_db.load_csv_predictions(csv_path)
                else:
                    predictions = self.prediction_db.load_today_predictions()
            
            if not predictions:
                logger.warning("⚠️  No predictions found for today")
                return
            
            # Login to Sportybet
            if not await self.login_sportybet():
                logger.error("❌ Failed to login to Sportybet")
                return
            
            # Navigate to today's games
            if not await self.navigate_to_today_games():
                logger.error("❌ Failed to navigate to today's games")
                return
            
            # Process all predictions
            added = await self.process_predictions(predictions)
            
            if added > 0:
                # Pause for review
                await self.pause_for_review()
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.close_browser()


async def main():
    """Main entry point"""
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Configuration
    SPORTYBET_USERNAME = "your_username"  # Change this
    SPORTYBET_PASSWORD = "your_password"  # Change this
    HEADLESS = False  # Set to True to run without visible browser
    
    # Initialize bot
    bot = SportybetBot(
        username=SPORTYBET_USERNAME,
        password=SPORTYBET_PASSWORD,
        headless=HEADLESS
    )
    
    # Run bot
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())

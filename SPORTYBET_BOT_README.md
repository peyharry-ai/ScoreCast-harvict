# Sportybet.gh Automated Betting Bot 🤖

Intelligent automated betting bot that integrates with ScoreCast predictions and automatically fills Sportybet betting slips with advanced anti-detection evasion.

## 🎯 Features

- ✅ **Automated Login** - Securely logs into Sportybet accounts
- ✅ **Prediction Integration** - Loads ScoreCast predictions for today's games
- ✅ **Smart Fixture Matching** - Matches predictions with Sportybet markets
- ✅ **Auto Slip Filling** - Automatically selects odds and adds to betslip
- ✅ **Anti-Detection Evasion** - Advanced stealth measures to avoid bot detection
  - Realistic human-like delays between actions
  - Random mouse movements
  - User agent rotation
  - Stealth mode Playwright configuration
  - Geolocation spoofing (Ghana)
  - Timezone & locale matching
- ✅ **Manual Review Pause** - Stops before submission for your review
- ✅ **Configuration File** - YAML-based configuration
- ✅ **Session Logging** - Comprehensive logs and session records
- ✅ **Safety Features** - Dry run mode, confidence filters, odds limits

## 📋 Requirements

- Python 3.10+
- Sportybet.gh account
- ScoreCast predictions data
- Playwright + Chromium browser

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-bot.txt
```

### 2. Install Playwright Browser

```bash
playwright install chromium
```

### 3. Configure Bot

Edit `Scripts/sportybet_config.yaml`:

```yaml
sportybet:
  username: "your_sportybet_username"
  password: "your_sportybet_password"
  headless: false  # true to run invisible

betting:
  stake_per_bet: 10.0  # in GHS
  min_odds: 1.5
  max_odds: 100.0
```

### 4. Prepare Predictions

The bot looks for predictions in:
- `Datasets/Predictions/` (JSON files)
- Or specify a CSV file path in config

**Prediction format (JSON):**
```json
[
  {
    "home": "Team A",
    "away": "Team B",
    "date": "2025-09-13T15:00:00",
    "prediction": "1",
    "market_type": "1X2",
    "odds": 2.45,
    "confidence": 0.75
  }
]
```

**Prediction format (CSV):**
```csv
home,away,date,prediction,market_type,odds,confidence
Team A,Team B,2025-09-13T15:00:00,1,1X2,2.45,0.75
```

### 5. Run the Bot

```bash
# Basic bot
python Scripts/sportybet_bot.py

# Advanced bot with config
python Scripts/sportybet_bot_advanced.py
```

## 🛡️ Anti-Detection Features

The bot implements multiple layers of detection evasion:

### 1. **Stealth Measures**
- Removes `navigator.webdriver` flag
- Hides browser automation signatures
- Matches locale/timezone to Ghana
- Realistic viewport size

### 2. **Human-Like Behavior**
- Random delays between actions (0.5-3 seconds)
- Realistic mouse movements
- Scrolling simulation
- Natural interaction patterns

### 3. **Request Patterns**
- User agent rotation (5 different agents)
- Network idle waiting
- Request rate limiting
- Realistic session duration

### 4. **Browser Context**
- Geolocation spoofing (Accra, Ghana coordinates)
- Language/locale set to Ghana English
- Timezone Africa/Accra
- Realistic permissions setup

## 📁 File Structure

```
Scripts/
├── sportybet_bot.py              # Core bot logic
├── sportybet_bot_advanced.py     # Advanced bot with config
├── sportybet_config.yaml         # Configuration file
└── ...existing files...

logs/
├── sportybet_bot.log            # Bot execution logs
├── screenshots/                 # Error screenshots
└── sessions/                    # Session records (JSON)
```

## 📝 Configuration Options

### Sportybet Settings
```yaml
sportybet:
  username: "your_username"
  password: "your_password"
  headless: false  # Show browser (true = hidden)
```

### Betting Settings
```yaml
betting:
  stake_per_bet: 10.0        # Amount per bet in GHS
  min_odds: 1.5              # Minimum odds to consider
  max_odds: 100.0            # Maximum odds to consider
  market_types:
    - "1X2"                  # Win/Draw/Loss
    - "BTTS"                 # Both Teams to Score
    - "O/U"                  # Over/Under
  auto_select:
    enable: true
    selection_threshold: 0.65  # Confidence minimum
```

### Database Settings
```yaml
database:
  predictions_dir: "Datasets/Predictions"
  csv_path: null  # Or path to CSV file
  filter_by_confidence: true
  min_confidence: 0.60
```

### Anti-Detection Settings
```yaml
anti_detection:
  realistic_delays: true
  min_delay: 0.5
  max_delay: 3.0
  random_mouse_movements: true
  rotate_user_agents: true
  use_residential_proxy: false  # Premium feature
  proxy_url: null
```

### Safety Settings
```yaml
safety:
  max_bets_per_day: 50
  pause_before_submit: true    # Pause for review
  dry_run: false               # Test mode (no actual bets)
  log_all_actions: true
```

## 🔄 Workflow

```
1. Launch Browser (with stealth)
   ↓
2. Login to Sportybet
   ↓
3. Navigate to Today's Games
   ↓
4. For each prediction:
   - Find fixture on Sportybet
   - Select prediction/odds
   - Add to betslip
   - Random human-like delay
   ↓
5. Pause for Manual Review
   ↓
6. User confirms and places bet
```

## 🚨 Safety & Ethics

⚠️ **Important Notes:**

- **Terms of Service**: Most betting sites forbid automated betting. Use at your own risk.
- **Account Risk**: Accounts can be banned if detected. Use stealth mode.
- **Legal**: Check local laws regarding automated betting in your jurisdiction.
- **Dry Run Mode**: Test with `dry_run: true` before actual use.
- **Manual Review**: Always review predictions before submission.

## 🐛 Troubleshooting

### Bot Not Finding Fixtures
- Check prediction data format
- Verify team names match exactly with Sportybet
- Check logs: `logs/sportybet_bot.log`

### Login Fails
- Verify username/password in config
- Check if account requires 2FA (manual login may be needed)
- Check for CAPTCHAs

### Odds Not Matching
- Odds may have changed since prediction
- Bot will pause for manual selection
- Review odds before confirmation

### Bot Detected
- Enable residential proxy (if available)
- Increase delays in config
- Add randomization to mouse movements
- Use in headless mode less frequently

### Screenshot Errors
- Check `logs/screenshots/` for error screenshots
- Verify browser viewport settings
- Check Sportybet UI changes

## 📊 Logging

All bot actions are logged to:
- **Console**: Real-time status updates
- **File**: `logs/sportybet_bot.log` - Detailed logs
- **Session**: `logs/sessions/session_*.json` - Session records

### View Logs

```bash
# Follow logs in real-time
tail -f logs/sportybet_bot.log

# View latest session
cat logs/sessions/session_*.json | jq
```

## 🔧 Advanced Usage

### Run with Custom Predictions

```python
from Scripts.sportybet_bot_advanced import AdvancedSportybetBot, ConfigManager

config = ConfigManager()
bot = AdvancedSportybetBot(config)

# Custom predictions
predictions = [
    {
        'home': 'Liverpool',
        'away': 'Manchester United',
        'date': '2025-09-13T15:00:00',
        'prediction': '1',
        'market_type': '1X2',
        'odds': 1.85,
        'confidence': 0.78
    }
]

await bot.run(predictions=predictions)
```

### Dry Run Mode (Test)

```yaml
safety:
  dry_run: true  # Doesn't actually place bets
```

```bash
python Scripts/sportybet_bot_advanced.py
```

### Scheduled Runs (Cron)

```bash
# Run bot every day at 10 AM
0 10 * * * cd /path/to/project && python Scripts/sportybet_bot_advanced.py
```

## 📚 API Reference

### SportybetBot Class

```python
class SportybetBot:
    async def launch_browser()      # Launch with stealth
    async def login_sportybet()     # Login to account
    async def navigate_to_today_games()  # Go to today's section
    async def find_fixture_on_sportybet(prediction)  # Find specific match
    async def select_market_and_odds(prediction)     # Select market
    async def add_to_betslip()      # Add to slip
    async def process_predictions(predictions)  # Process all preds
    async def pause_for_review()    # Wait for user review
    async def run()                 # Main execution
```

### PredictionDatabase Class

```python
class PredictionDatabase:
    def load_today_predictions()    # Load from JSON
    def load_csv_predictions(path)  # Load from CSV
```

### AntiDetectionModule

```python
class AntiDetectionModule:
    @staticmethod
    async def human_delay(min, max)         # Realistic delay
    @staticmethod
    async def scroll_page(page)             # Simulate scrolling
    @staticmethod
    async def random_mouse_movement(page)   # Random mouse moves
    @staticmethod
    def get_random_user_agent()             # Rotate user agent
```

## 🎓 Examples

### Example 1: Load Today's Predictions and Run

```bash
python Scripts/sportybet_bot_advanced.py
```

### Example 2: Run in Headless Mode

Edit `sportybet_config.yaml`:
```yaml
sportybet:
  headless: true
```

```bash
python Scripts/sportybet_bot_advanced.py
```

### Example 3: Filter by Confidence

Edit `sportybet_config.yaml`:
```yaml
database:
  min_confidence: 0.75  # Only high-confidence predictions
```

### Example 4: Test Mode (Dry Run)

Edit `sportybet_config.yaml`:
```yaml
safety:
  dry_run: true  # Won't place actual bets
```

## 📞 Support & Issues

If you encounter issues:

1. **Check logs**: `logs/sportybet_bot.log`
2. **Screenshot**: Error screenshots in `logs/screenshots/`
3. **Test mode**: Run with `dry_run: true`
4. **Manual login**: Try logging in manually first to check account status
5. **Sportybet UI**: Verify Sportybet website hasn't changed

## 🔐 Security

- Never commit credentials to git
- Use environment variables for sensitive data:

```bash
export SPORTYBET_USERNAME="your_username"
export SPORTYBET_PASSWORD="your_password"
```

Then in config:
```python
import os
username = os.getenv('SPORTYBET_USERNAME', 'default')
```

- Delete password from config file after testing
- Use strong, unique passwords
- Enable 2FA on Sportybet if possible

## 📄 License

MIT - Feel free to use, modify, and distribute

## ⚠️ Disclaimer

This bot is for **educational and automation purposes only**. Users are responsible for:
- Compliance with Sportybet's Terms of Service
- Local gambling laws and regulations
- Responsible gambling practices
- Account security and any resulting consequences

**Use at your own risk.**

---

**Made with ❤️ for ScoreCast | Football Prediction & Automation**

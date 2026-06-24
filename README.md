# 📈 StockSense AI

AI-powered stock trading bot · Claude Sonnet + Alpaca Paper Trading · Auto GitHub sync

## Quick start
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
python app.py          # dashboard → http://localhost:5000
python scheduler.py    # auto-trader (9:31 AM + 3:45 PM ET)
```

## Stack
- AI: Anthropic Claude Sonnet 4.6
- Market data: yfinance
- Broker: Alpaca paper trading
- Web: Flask
- Scheduler: schedule + pytz
- CI/CD: GitHub Actions

## API Keys needed
- Alpaca: https://app.alpaca.markets (free paper trading)
- Anthropic: https://console.anthropic.com/keys

## ⚠️ Disclaimer
Paper trading only by default. Do not risk real money without extensive testing.

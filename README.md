# 📈 StockSense AI

> AI-powered stock analysis and paper trading bot — Claude Sonnet + Alpaca + Interactive Dashboard

[![Version](https://img.shields.io/badge/version-v1.0.1-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Features

- **AI Signals** — Claude Sonnet analyzes RSI, MACD, Bollinger Bands, SMA 20/50, volume
- **Interactive Dashboard** — Real-time portfolio, signal cards, P&L charts, watchlist manager
- **Paper Trading** — Alpaca paper trading API with auto-execution
- **Scheduler** — Twice-daily analysis runs at market open (9:31 AM) and close (3:45 PM ET)
- **GitHub Auto-sync** — Commits and tags results after each analysis run

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in API keys
python app.py               # dashboard → http://localhost:5000
python scheduler.py         # auto-trader (9:31 AM + 3:45 PM ET)
```

## Dashboard

Open `http://localhost:5000` after starting the Flask server.

| Tab | Description |
|-----|-------------|
| **Overview** | Portfolio stats, signal distribution chart, top signals, open positions |
| **Portfolio** | Full positions table with P&L, portfolio bar chart |
| **Signals** | AI signal cards with confidence bars, target/stop prices, reasoning |
| **Watchlist** | Manage tickers, analyze individual stocks on-demand |
| **Logs** | Live analyzer log viewer |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/signals` | Latest AI signals JSON |
| `GET` | `/api/portfolio` | Alpaca account + positions |
| `POST` | `/api/analyze` | Trigger analysis run |
| `GET` | `/api/ticker/:symbol` | Analyze a single ticker |
| `GET/POST` | `/api/watchlist` | Get or update watchlist |
| `GET` | `/api/logs` | Last 100 log lines |

## Stack

| Layer | Tech |
|-------|------|
| AI | Anthropic Claude Sonnet 4.6 |
| Market Data | yfinance |
| Broker | Alpaca paper trading |
| Backend | Flask + Flask-CORS |
| Frontend | Vanilla JS + Tailwind CSS + Chart.js |
| Scheduler | schedule + pytz |
| CI/CD | GitHub Actions |

## Environment Variables

```env
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
ANTHROPIC_API_KEY=your_anthropic_key
```

Get keys:
- Alpaca: https://app.alpaca.markets (free paper trading)
- Anthropic: https://console.anthropic.com/keys

## ⚠️ Disclaimer

Paper trading only by default. Never risk real capital without extensive backtesting and risk management.

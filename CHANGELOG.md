# Changelog

All notable changes to StockSense AI are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.1] - 2026-06-25

### Added
- **Interactive Dashboard** (`frontend/index.html`) — full single-page UI served by Flask
  - Sidebar navigation with 5 tabs: Overview, Portfolio, Signals, Watchlist, Logs
  - Overview tab: portfolio stat cards (value, day P&L, buying power, open positions), signal distribution doughnut chart, latest signals preview, open positions quick-view
  - Portfolio tab: full positions table with qty, avg cost, current price, P&L, P&L %, value; horizontal bar chart of P&L per position
  - Signals tab: filterable AI signal cards with confidence bars, reasoning text, target/stop prices, time horizon
  - Watchlist tab: add/remove tickers, on-demand single-ticker analysis with result card
  - Logs tab: scrollable log viewer with color-coded INFO/ERROR/WARNING lines
- **Auto-refresh** — 60-second countdown with manual refresh button
- **Toast notifications** — success/error/info feedback for all async actions
- **Run Analysis button** — triggers background analysis from the UI
- `CHANGELOG.md` — this file
- Updated `README.md` with dashboard documentation and API endpoint table

### Changed
- README rewritten with full feature list, dashboard tab guide, and API reference table

### Fixed
- No bug fixes in this release (first dashboard release)

---

## [v1.0.0] - 2026-06-24

### Added
- Initial project setup
- Flask REST API (`app.py`) with endpoints: `/api/signals`, `/api/portfolio`, `/api/analyze`, `/api/ticker/:symbol`, `/api/watchlist`, `/api/logs`, `/api/github/push`
- Core analyzer (`backend/analyzer.py`) with six technical indicators: RSI, MACD, Bollinger Bands, SMA 20/50, volume analysis
- Alpaca paper trading integration — auto-execute BUY/SELL orders based on AI signals
- yfinance market data fetching with 60-day lookback
- Claude Sonnet 4.6 AI signal generation (BUY/SELL/HOLD with confidence score, reasoning, target/stop)
- Scheduler (`scheduler.py`) — twice-daily runs at 9:31 AM and 3:45 PM ET on market days
- GitHub auto-push script (`scripts/git_push.sh`)
- GitHub Actions workflow (`deploy.yml`)
- `.env.example` with required environment variables
- Default watchlist: AAPL, NVDA, MSFT, GOOGL, META, TSLA, AMZN, AMD, PLTR, SPY

[v1.0.1]: https://github.com/ntcrash/stocksense-ai/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/ntcrash/stocksense-ai/releases/tag/v1.0.0

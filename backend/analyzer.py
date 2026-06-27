"""
StockSense AI - Core Stock Analyzer
Fetches market data, runs AI analysis, generates buy/sell/hold signals.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import anthropic
import alpaca_trade_api as tradeapi
import yfinance as yf
import pandas as pd
import numpy as np

logging.basicConfig(
    filename="logs/analyzer.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

WATCHLIST = [
    "AAPL", "NVDA", "MSFT", "GOOGL", "META",
    "TSLA", "AMZN", "AMD", "PLTR", "SPY"
]

ALPACA_API_KEY    = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL   = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

MAX_POSITION_PCT  = 0.10
MIN_CONFIDENCE    = 0.70
STOP_LOSS_PCT     = 0.05


def get_alpaca_client():
    return tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")


def fetch_stock_data(ticker: str, days: int = 120) -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data and compute technical indicators.
    days=120 ensures ~85 trading days — enough for SMA_50 + buffer after dropna().
    Handles yfinance >= 0.2.38 MultiIndex column format automatically.
    """
    try:
        end   = datetime.now()
        start = end - timedelta(days=days)
        df    = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

        if df.empty:
            log.warning(f"No data returned for {ticker}")
            return None

        # Fix: yfinance >= 0.2.38 returns MultiIndex columns like ('Close', 'AAPL').
        # Flatten to single-level so df["Close"] works correctly.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Guard: ensure required columns exist
        required = {"Close", "High", "Low", "Open", "Volume"}
        missing  = required - set(df.columns)
        if missing:
            log.error(f"Missing columns for {ticker}: {missing}")
            return None

        df["SMA_20"]     = df["Close"].rolling(20).mean()
        df["SMA_50"]     = df["Close"].rolling(50).mean()
        df["RSI"]        = _compute_rsi(df["Close"])
        df["MACD"], df["Signal"] = _compute_macd(df["Close"])
        df["BB_upper"], df["BB_lower"] = _compute_bollinger(df["Close"])
        df["Volume_MA"]  = df["Volume"].rolling(20).mean()
        df["Pct_Change"] = df["Close"].pct_change()

        df_clean = df.dropna()
        if df_clean.empty:
            log.warning(f"All rows dropped after indicator calculation for {ticker} — insufficient history")
            return None

        log.info(f"Fetched {len(df_clean)} rows for {ticker}")
        return df_clean

    except Exception as e:
        log.error(f"Error fetching {ticker}: {e}")
        return None


def _compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta  = prices.diff()
    gain   = delta.clip(lower=0).rolling(period).mean()
    loss   = (-delta.clip(upper=0)).rolling(period).mean()
    rs     = gain / loss
    return 100 - (100 / (1 + rs))


def _compute_macd(prices: pd.Series):
    ema12  = prices.ewm(span=12).mean()
    ema26  = prices.ewm(span=26).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal


def _compute_bollinger(prices: pd.Series, period: int = 20, std: float = 2.0):
    sma    = prices.rolling(period).mean()
    stddev = prices.rolling(period).std()
    return sma + std * stddev, sma - std * stddev


def build_analysis_prompt(ticker: str, df: pd.DataFrame) -> str:
    recent = df.tail(10)
    last   = df.iloc[-1]
    return f"""Analyze {ticker} stock and provide a trading signal.

Price: ${float(last['Close']):.2f} | RSI: {float(last['RSI']):.1f} | MACD: {float(last['MACD']):.4f}
SMA20: ${float(last['SMA_20']):.2f} | SMA50: ${float(last['SMA_50']):.2f}
BB Upper: ${float(last['BB_upper']):.2f} | BB Lower: ${float(last['BB_lower']):.2f}
Volume ratio: {float(last['Volume'] / last['Volume_MA']):.2f}x avg

Recent 10-day data:
{recent[['Close','RSI','MACD','Pct_Change']].to_string()}

Respond ONLY with valid JSON:
{{"signal": "BUY"|"SELL"|"HOLD", "confidence": 0.0-1.0, "reasoning": "2-3 sentences",
  "target_price": float, "stop_loss": float, "time_horizon": "1-3 days"|"1 week"|"2+ weeks"}}"""


def get_ai_signal(ticker: str, df: pd.DataFrame) -> Optional[dict]:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": build_analysis_prompt(ticker, df)}]
        )
        raw  = resp.content[0].text.strip()
        data = json.loads(raw)
        data["ticker"]    = ticker
        data["price"]     = float(df.iloc[-1]["Close"])
        data["timestamp"] = datetime.now().isoformat()
        log.info(f"Signal for {ticker}: {data['signal']} @ {data['confidence']:.0%}")
        return data
    except json.JSONDecodeError as e:
        log.error(f"JSON parse error for {ticker}: {e} | raw: {raw[:200]}")
        return None
    except Exception as e:
        log.error(f"AI signal error for {ticker}: {e}")
        return None


def execute_trade(api, signal: dict):
    ticker, action, confidence = signal["ticker"], signal["signal"], signal["confidence"]
    if action == "HOLD" or confidence < MIN_CONFIDENCE:
        return
    portfolio_val = float(api.get_account().portfolio_value)
    qty = int((portfolio_val * MAX_POSITION_PCT) // signal["price"])
    if qty < 1:
        return
    try:
        if action == "BUY":
            try:
                api.get_position(ticker)
                return  # Already holding
            except Exception:
                pass
            api.submit_order(symbol=ticker, qty=qty, side="buy", type="market", time_in_force="day")
            log.info(f"BUY {qty}x {ticker}")
        elif action == "SELL":
            try:
                pos = api.get_position(ticker)
                api.submit_order(symbol=ticker, qty=abs(int(pos.qty)), side="sell", type="market", time_in_force="day")
                log.info(f"SELL {pos.qty}x {ticker}")
            except Exception:
                pass
    except Exception as e:
        log.error(f"Order error for {ticker}: {e}")


def save_signals(signals: list):
    os.makedirs("data", exist_ok=True)
    with open("data/latest_signals.json", "w") as f:
        json.dump({"generated_at": datetime.now().isoformat(), "signals": signals}, f, indent=2)


def run_analysis(execute: bool = True):
    log.info("=== StockSense AI analysis started ===")
    api = get_alpaca_client()
    signals = []
    for ticker in WATCHLIST:
        df = fetch_stock_data(ticker)  # uses default 120 days
        if df is not None and len(df) >= 50:
            signal = get_ai_signal(ticker, df)
            if signal:
                signals.append(signal)
                if execute:
                    execute_trade(api, signal)
    save_signals(signals)
    log.info(f"=== Complete: {len(signals)}/{len(WATCHLIST)} ===")
    return signals


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_analysis(execute=not args.dry_run)

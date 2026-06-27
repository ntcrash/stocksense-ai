"""
StockSense AI - Flask API Server
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json, os, subprocess, threading
from datetime import datetime
from backend.analyzer import run_analysis, fetch_stock_data, get_ai_signal, WATCHLIST

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/api/signals")
def get_signals():
    path = "data/latest_signals.json"
    if not os.path.exists(path):
        return jsonify({"error": "No signals yet. Run analysis first."}), 404
    with open(path) as f:
        return jsonify(json.load(f))

@app.route("/api/portfolio")
def get_portfolio():
    try:
        import alpaca_trade_api as tradeapi
        api = tradeapi.REST(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"),
                            os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"), api_version="v2")
        account = api.get_account()
        positions = api.list_positions()
        return jsonify({
            "portfolio_value": float(account.portfolio_value),
            "buying_power":    float(account.buying_power),
            "day_pl":          float(account.equity) - float(account.last_equity),
            "positions": [{"symbol": p.symbol, "qty": float(p.qty), "avg_cost": float(p.avg_entry_price),
                           "current": float(p.current_price), "pl": float(p.unrealized_pl),
                           "pl_pct": float(p.unrealized_plpc)} for p in positions]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze", methods=["POST"])
def trigger_analysis():
    dry_run = request.json.get("dry_run", True) if request.json else True
    threading.Thread(target=lambda: run_analysis(execute=not dry_run), daemon=True).start()
    return jsonify({"status": "started", "dry_run": dry_run, "timestamp": datetime.now().isoformat()})

@app.route("/api/ticker/<symbol>")
def get_ticker(symbol: str):
    symbol = symbol.upper()
    df = fetch_stock_data(symbol, days=30)
    if df is None:
        return jsonify({"error": f"Could not fetch data for {symbol}"}), 404
    return jsonify(get_ai_signal(symbol, df) or {"error": "AI analysis failed"})

@app.route("/api/watchlist", methods=["GET", "POST"])
def manage_watchlist():
    path = "data/watchlist.json"
    if request.method == "GET":
        if os.path.exists(path):
            with open(path) as f:
                return jsonify(json.load(f))
        return jsonify({"tickers": WATCHLIST})
    tickers = request.json.get("tickers", [])
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump({"tickers": [t.upper() for t in tickers]}, f)
    return jsonify({"saved": True, "tickers": tickers})

@app.route("/api/logs")
def get_logs():
    path = "logs/analyzer.log"
    if not os.path.exists(path):
        return jsonify({"lines": []})
    with open(path) as f:
        return jsonify({"lines": f.readlines()[-100:]})

@app.route("/api/github/push", methods=["POST"])
def github_push():
    try:
        msg = (request.json or {}).get("message", f"Auto-update {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        result = subprocess.run(["bash", "scripts/git_push.sh", msg], capture_output=True, text=True, timeout=30)
        return jsonify({"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 8080)), host="0.0.0.0")

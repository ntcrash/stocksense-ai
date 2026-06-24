"""
StockSense AI - Scheduler
Runs analysis at market open (9:31 AM) and market close (3:45 PM) ET.
"""
import schedule, time, logging, subprocess, sys
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[logging.FileHandler("logs/scheduler.log"), logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

MARKET_TZ = pytz.timezone("America/New_York")
GITHUB_AUTO_PUSH = True


def is_market_day() -> bool:
    return datetime.now(MARKET_TZ).weekday() < 5


def _git_push(message: str):
    try:
        result = subprocess.run(["bash", "scripts/git_push.sh", message],
                                capture_output=True, text=True, timeout=30)
        log.info("GitHub push success" if result.returncode == 0 else f"Push failed: {result.stderr}")
    except Exception as e:
        log.error(f"Git push error: {e}")


def run_open_scan():
    if not is_market_day():
        return
    log.info("=== OPEN SCAN STARTING ===")
    result = subprocess.run([sys.executable, "-m", "backend.analyzer"], timeout=300)
    log.info(f"Open scan complete (exit {result.returncode})")
    if GITHUB_AUTO_PUSH:
        _git_push("Auto: morning scan results")


def run_close_scan():
    if not is_market_day():
        return
    log.info("=== CLOSE SCAN STARTING ===")
    result = subprocess.run([sys.executable, "-m", "backend.analyzer"], timeout=300)
    log.info(f"Close scan complete (exit {result.returncode})")
    if GITHUB_AUTO_PUSH:
        _git_push("Auto: afternoon scan results")


schedule.every().day.at("09:31").do(run_open_scan)
schedule.every().day.at("15:45").do(run_close_scan)

log.info("Scheduler started. Runs at 09:31 and 15:45 ET on market days.")

if __name__ == "__main__":
    log.info("Running initial dry-run...")
    subprocess.run([sys.executable, "-m", "backend.analyzer", "--dry-run"], timeout=300)
    while True:
        schedule.run_pending()
        time.sleep(30)

import time
import requests
import undetected_chromedriver as uc
from datetime import datetime, timedelta, timezone
from MEXCDriver import MEXCDriver

BASE = "https://contract.mexc.com/api/v1"
SYMBOL = "ASR_USDT"
OPEN_LEAD = 10
CLOSE_DELAY = 0
CYCLE_HOURS = [0, 4, 8, 12, 16, 20]

op = uc.ChromeOptions()
op.add_argument(r'--user-data-dir=C:\Users\lceorange\Desktop\mexc_test\main_userdata')
mexc = MEXCDriver(startup_url=f"https://www.mexc.com/zh-TW/futures/{SYMBOL}?type=linear_swap", options=op)

### ---- API 包裝 ----
def server_time_ms() -> int:
    return int(requests.get(f"{BASE}/contract/ping", timeout=5).json()["data"])

def funding_rate(sym: str) -> float:
    r = requests.get(f"{BASE}/contract/funding_rate/{sym}", timeout=5)
    r.raise_for_status()
    return float(r.json()["data"]["fundingRate"])

# ★ 把下單與平倉邏輯換成你自己的簽名 API ★
def place_order(sym: str, side: str):
    print(f"[{utc_now()}] OPEN {side} {sym}")
    try:
        mexc.max_slider()
        time.sleep(1)
    except Exception as e:
        print("Error:", e)
    
    if side == "BUY":
        mexc.buy()
    else:
        mexc.sell()
    mexc.scroll_to_bottom()

def close_position(sym: str):
    print(f"[{utc_now()}] CLOSE {sym} (market)")
    mexc.flash_close_position()
    mexc.scroll_to_top()

### ---- 時間計算 ----
def next_cycle_ts(ts_ms: int) -> int:
    now = datetime.fromtimestamp(ts_ms/1000, tz=timezone.utc)
    base_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for day_shift in (0, 1):
        d0 = base_day + timedelta(days=day_shift)
        for h in CYCLE_HOURS:
            ct = d0 + timedelta(hours=h)
            if ct > now:
                return int(ct.timestamp()*1000)
    raise RuntimeError("找不到下一個 cycle")

def test_cycle_ts(ts_ms: int) -> int:
    """
    Returns the timestamp of the next 5-minute cycle.
    Example: 12:05, 12:10, 12:15, etc.
    """
    now = datetime.fromtimestamp(ts_ms/1000, tz=timezone.utc)
    # Round to the next 5-minute mark
    minutes = now.minute
    next_5min = ((minutes // 5) + 1) * 5
    
    # If we're already at a 5-minute mark or past it, move to the next one
    if next_5min >= 60:
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        next_time = next_hour
    else:
        next_time = now.replace(minute=next_5min, second=0, microsecond=0)
    
    # If we're exactly at the time or slightly past it, move to the next cycle
    if next_time <= now:
        next_time = next_time + timedelta(minutes=5)
        
    return int(next_time.timestamp()*1000)

def utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

### ---- 主迴圈 ----
def main():
    while True:
        try:
            now_ms = server_time_ms()
            cycle_ms = next_cycle_ts(now_ms)
            open_ms  = cycle_ms - OPEN_LEAD*1000
            close_ms = cycle_ms + CLOSE_DELAY*1000

            print(f"[{utc_now()}] open_ms: {open_ms}")
            print(f"[{utc_now()}] close_ms: {close_ms}")
            print(f"[{utc_now()}] now_ms: {now_ms}")
            print(f"[{utc_now()}] cycle_ms: {cycle_ms}")
            print(f"[{utc_now()}] 等待開倉時間: {max(0, (open_ms - now_ms)/1000)}s")

            # ---- 等待到 open_ms ----
            time.sleep(max(0, (open_ms - now_ms)/1000))

            rate = funding_rate(SYMBOL)
            if rate <= -0.005:
                side = "BUY"
                place_order(SYMBOL, side)

                # ---- 等待到 close_ms ----
                now_ms = server_time_ms()
                print(f"[{utc_now()}] 等待平倉時間: {max(0, (close_ms - now_ms)/1000)}s")
                time.sleep(max(0, (close_ms - now_ms)/1000))
                close_position(SYMBOL)
                time.sleep(5)

        except Exception as e:
            print("Error:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()
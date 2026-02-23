# -*- coding: utf-8 -*-
"""
GitHub Actions가 주기적으로 실행하는 주가 데이터 수집 스크립트.
watchlist.json의 종목 목록을 읽어 pykrx로 시세를 수집하고
data/prices.json에 저장합니다.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import os
from datetime import datetime
from pykrx import stock

BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATCHLIST_FILE = os.path.join(BASE_DIR, "watchlist.json")
OUTPUT_FILE    = os.path.join(BASE_DIR, "data", "prices.json")


def fetch_price(ticker: str, name: str) -> dict | None:
    today      = datetime.today().strftime("%Y%m%d")
    start_date = "20000101"
    try:
        df = stock.get_market_ohlcv_by_date(start_date, today, ticker)
        if df is None or df.empty:
            df = stock.get_etf_ohlcv_by_date(start_date, today, ticker)
        if df is None or df.empty:
            return None

        current_price = int(df["종가"].iloc[-1])
        ath           = int(df["고가"].max())
        ath_date      = df["고가"].idxmax().strftime("%Y-%m-%d")
        ratio         = round((current_price / ath) * 100, 2)

        return {
            "current_price":      current_price,
            "all_time_high":      ath,
            "all_time_high_date": ath_date,
            "ratio":              ratio,
        }
    except Exception as e:
        print(f"  ⚠  [{name}({ticker})] 실패: {e}")
        return None


def main():
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        watchlist = json.load(f)["stocks"]

    prices = {}
    for item in watchlist:
        print(f"  → {item['name']} ({item['ticker']}) 조회 중...")
        info = fetch_price(item["ticker"], item["name"])
        if info:
            prices[item["ticker"]] = info
            print(f"     현재가: {info['current_price']:,}원  /  역대최고가: {info['all_time_high']:,}원")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    output = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prices":     prices,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(prices)}/{len(watchlist)}개 종목 업데이트 완료 → data/prices.json")


if __name__ == "__main__":
    main()

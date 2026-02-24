from pykrx import stock
from datetime import datetime


def get_stock_info(ticker: str, name: str) -> dict | None:
    """종목코드와 이름을 받아 현재가, 역대 최고가 정보를 반환."""
    today      = datetime.today().strftime("%Y%m%d")
    start_date = "20000101"

    try:
        df = stock.get_market_ohlcv_by_date(start_date, today, ticker)

        if df is None or df.empty:
            df = stock.get_etf_ohlcv_by_date(start_date, today, ticker)

        if df is None or df.empty:
            return None

        current_price = int(df["종가"].iloc[-1])
        all_time_high = int(df["고가"].max())
        ath_date      = df["고가"].idxmax().strftime("%Y-%m-%d")
        ratio         = round((current_price / all_time_high) * 100, 2)

        return {
            "current_price":      current_price,
            "all_time_high":      all_time_high,
            "all_time_high_date": ath_date,
            "ratio":              ratio,
        }

    except Exception as e:
        print(f"  ⚠  [{name}({ticker})] 조회 실패: {e}")
        return None


def _recent_trading_day() -> str:
    """오늘 또는 가장 최근 거래일을 YYYYMMDD 형식으로 반환."""
    from datetime import timedelta
    d = datetime.today()
    # 토·일이면 금요일로 이동
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")


def search_stocks(keyword: str) -> list[tuple]:
    """종목명 키워드로 코스피·코스닥·ETF 종목 검색. 반환: [(코드, 이름, 시장), ...]"""
    results = []
    today   = _recent_trading_day()
    kw      = keyword.lower()

    # ── 코스피 / 코스닥 ──────────────────────────────
    try:
        for market in ("KOSPI", "KOSDAQ"):
            tickers = stock.get_market_ticker_list(today, market=market)
            for t in tickers:
                try:
                    n = stock.get_market_ticker_name(t)
                    if n and kw in n.lower():
                        results.append((t, n, market))
                except Exception:
                    continue
    except Exception as e:
        print(f"  ⚠  일반종목 검색 오류: {e}")

    # ── ETF ─────────────────────────────────────────
    try:
        etf_tickers = stock.get_etf_ticker_list(today)
        for t in etf_tickers:
            try:
                n = stock.get_etf_ticker_name(t)  # ETF 전용 이름 조회 API
                if n and kw in n.lower():
                    results.append((t, n, "ETF"))
            except Exception:
                continue
    except Exception as e:
        print(f"  ⚠  ETF 검색 오류: {e}")

    return results

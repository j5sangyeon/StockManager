import json
import os
from flask import Flask, jsonify, request, render_template
from stock_manager import get_stock_info, search_stocks

app = Flask(__name__)

PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "portfolio.json")

DEFAULT_WATCHLIST = [
    {"ticker": "000660", "name": "SK하이닉스",             "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "028260", "name": "삼성물산",               "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "064350", "name": "현대로템",               "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "079550", "name": "LIG넥스원",              "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "140860", "name": "파크시스템스",            "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "469160", "name": "PLUS 고배당주",           "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "449450", "name": "SOL금융지주플러스고배당", "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "411060", "name": "ACE KRX금현물",          "quantity": 0, "buy_price": 0, "sell_target": 0},
    {"ticker": "005930", "name": "삼성전자",               "quantity": 0, "buy_price": 0, "sell_target": 0},
]

# ─────────────────────────────────────────────
#  포트폴리오 로드 / 저장
# ─────────────────────────────────────────────

def load_portfolio() -> list:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)["watchlist"]
    _save(DEFAULT_WATCHLIST)
    return DEFAULT_WATCHLIST


def _save(watchlist: list) -> None:
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump({"watchlist": watchlist}, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  라우트
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/portfolio", methods=["GET"])
def api_get_portfolio():
    return jsonify(load_portfolio())


@app.route("/api/stock/<ticker>", methods=["GET"])
def api_get_stock(ticker):
    name = request.args.get("name", ticker)
    info = get_stock_info(ticker, name)
    if info:
        return jsonify(info)
    return jsonify({"error": "데이터를 가져올 수 없습니다."}), 404


@app.route("/api/portfolio", methods=["POST"])
def api_add_stock():
    data = request.get_json()
    if not data or not data.get("ticker") or not data.get("name"):
        return jsonify({"error": "종목코드와 종목명은 필수입니다."}), 400

    watchlist = load_portfolio()
    for item in watchlist:
        if item["ticker"] == data["ticker"]:
            return jsonify({"error": "이미 등록된 종목입니다."}), 400

    watchlist.append({
        "ticker":      data["ticker"].strip(),
        "name":        data["name"].strip(),
        "quantity":    int(data.get("quantity") or 0),
        "buy_price":   int(data.get("buy_price") or 0),
        "sell_target": int(data.get("sell_target") or 0),
    })
    _save(watchlist)
    return jsonify({"success": True})


@app.route("/api/portfolio/<ticker>", methods=["PUT"])
def api_update_stock(ticker):
    data = request.get_json()
    watchlist = load_portfolio()
    for item in watchlist:
        if item["ticker"] == ticker:
            item["quantity"]    = int(data.get("quantity")    or 0)
            item["buy_price"]   = int(data.get("buy_price")   or 0)
            item["sell_target"] = int(data.get("sell_target") or 0)
            _save(watchlist)
            return jsonify({"success": True})
    return jsonify({"error": "종목을 찾을 수 없습니다."}), 404


@app.route("/api/portfolio/<ticker>", methods=["DELETE"])
def api_delete_stock(ticker):
    watchlist = load_portfolio()
    _save([item for item in watchlist if item["ticker"] != ticker])
    return jsonify({"success": True})


@app.route("/api/search", methods=["GET"])
def api_search():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify([])
    results = search_stocks(keyword)
    return jsonify([{"ticker": t, "name": n, "market": m} for t, n, m in results])


if __name__ == "__main__":
    print("\n🚀  http://127.0.0.1:5000  에서 실행 중입니다.\n")
    app.run(debug=False, port=5000)

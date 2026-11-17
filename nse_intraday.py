#!/usr/bin/env python3
"""Live intraday NSE F&O opening-range scan (5-minute Yahoo bars).

CALL: price above the 9:15-9:30 high, above yesterday's close, and above the day's average price (VWAP).
PUT : price below the 9:15-9:30 low, below yesterday's close, and below VWAP.
A scan lists charts that match a rule. It is not a prediction or advice.
"""
import json, time, urllib.request, urllib.parse, datetime
from nse_scan import FNO, UA

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def bars(sym):
    for host in ("query2", "query1"):
        url = "https://%s.finance.yahoo.com/v8/finance/chart/%s.NS?range=1d&interval=5m" % (host, urllib.parse.quote(sym))
        for _ in range(2):
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20))["chart"]["result"][0]
                q = r["indicators"]["quote"][0]
                rows = [(t, h, l, c, v) for t, h, l, c, v in zip(r["timestamp"], q["high"], q["low"], q["close"], q["volume"]) if None not in (h, l, c, v)]
                return r["meta"], rows
            except Exception:
                time.sleep(3)
    return None, None


def main():
    hits, failed = [], []
    for s in FNO:
        meta, rows = bars(s)
        time.sleep(0.6)
        if not rows or len(rows) < 4:
            failed.append(s); continue
        orb = rows[:3]                                   # 9:15, 9:20, 9:25 bars
        orh, orl = max(b[1] for b in orb), min(b[2] for b in orb)
        price = meta.get("regularMarketPrice") or rows[-1][3]
        prev = meta.get("chartPreviousClose")
        vol = sum(b[4] for b in rows)
        vwap = sum((b[1] + b[2] + b[3]) / 3 * b[4] for b in rows) / vol if vol else price
        chg = (price / prev - 1) * 100 if prev else 0
        rng = (orh - orl) / price * 100
        side = None
        if price > orh and price > prev and price > vwap: side = "CALL"
        if price < orl and price < prev and price < vwap: side = "PUT"
        if side:
            stop = orl if side == "CALL" else orh
            risk = abs(price - stop) / price * 100
            hits.append(dict(sym=s, side=side, price=round(price, 2), chg=round(chg, 2), orh=round(orh, 2),
                             orl=round(orl, 2), vwap=round(vwap, 2), stop=round(stop, 2), risk=round(risk, 2),
                             turnover_cr=round(price * vol / 1e7, 1)))
    hits.sort(key=lambda h: -abs(h["chg"]) * min(h["turnover_cr"], 500))
    now = datetime.datetime.now(IST).strftime("%d %b %H:%M IST")
    print("%s  scanned %d, failed %d, setups %d" % (now, len(FNO) - len(failed), len(failed), len(hits)))
    print("%-11s %-4s %9s %6s %9s %9s %9s %9s %5s %7s" % ("SYMBOL", "SIDE", "PRICE", "CHG%", "OR-HIGH", "OR-LOW", "VWAP", "STOP", "RISK%", "TO-Cr"))
    for h in hits:
        print("%-11s %-4s %9.2f %6.2f %9.2f %9.2f %9.2f %9.2f %5.2f %7.1f" % (h["sym"], h["side"], h["price"], h["chg"], h["orh"], h["orl"], h["vwap"], h["stop"], h["risk"], h["turnover_cr"]))
    if failed: print("failed:", " ".join(failed))


if __name__ == "__main__":
    main()

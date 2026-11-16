#!/usr/bin/env python3
"""Next-day NSE F&O setup scan (daily bars from Yahoo Finance, .NS symbols).

A scan lists charts that match a rule. It is not a prediction or advice.
Usage: python3 nse_scan.py [--show 10]
"""
import argparse, json, time, urllib.request

FNO = """RELIANCE HDFCBANK ICICIBANK INFY TCS SBIN BHARTIARTL ITC LT KOTAKBANK AXISBANK
HINDUNILVR BAJFINANCE MARUTI SUNPHARMA TATAMOTORS M&M NTPC POWERGRID TITAN ULTRACEMCO
ASIANPAINT ADANIENT ADANIPORTS ONGC COALINDIA JSWSTEEL TATASTEEL HCLTECH WIPRO TECHM
BAJAJFINSV NESTLEIND GRASIM HINDALCO DRREDDY CIPLA EICHERMOT HEROMOTOCO BAJAJ-AUTO
BRITANNIA APOLLOHOSP DIVISLAB SBILIFE HDFCLIFE INDUSINDBK BPCL TATACONSUM SHRIRAMFIN
TRENT BEL HAL DLF VEDL BANKBARODA PNB CANBK IOC GAIL TATAPOWER DMART ZOMATO
LTIM PIDILITIND SIEMENS ABB GODREJCP DABUR HAVELLS AMBUJACEM CHOLAFIN JIOFIN
IRCTC INDIGO PFC RECLTD BHEL SAIL NMDC TVSMOTOR LUPIN AUROPHARMA BANDHANBNK
IDFCFIRSTB FEDERALBNK AUBANK POLYCAB DIXON PERSISTENT COFORGE MPHASIS""".split()

UA = "Mozilla/5.0 (compatible; nse-scan/1.0)"


def fetch(sym):
    for host in ("query2", "query1"):
        url = "https://%s.finance.yahoo.com/v8/finance/chart/%s.NS?range=6mo&interval=1d" % (
            host, urllib.parse.quote(sym))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.load(r)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            rows = [(h, l, c, v) for h, l, c, v in zip(q["high"], q["low"], q["close"], q["volume"])
                    if None not in (h, l, c, v)]
            return rows
        except Exception:
            continue
    return None


def ema(xs, n):
    k, e = 2 / (n + 1), xs[0]
    for x in xs[1:]:
        e = x * k + e * (1 - k)
    return e


def rsi(cl, n=14):
    g = l = 0.0
    for i in range(1, n + 1):
        d = cl[i] - cl[i - 1]; g += max(d, 0); l += max(-d, 0)
    g /= n; l /= n
    for i in range(n + 1, len(cl)):
        d = cl[i] - cl[i - 1]
        g = (g * (n - 1) + max(d, 0)) / n; l = (l * (n - 1) + max(-d, 0)) / n
    return 100 if l == 0 else 100 - 100 / (1 + g / l)


def analyse(sym, rows):
    if len(rows) < 60:
        return None
    hi, lo, cl, vo = zip(*rows)
    c = cl[-1]
    trs = [max(hi[i] - lo[i], abs(hi[i] - cl[i - 1]), abs(lo[i] - cl[i - 1])) for i in range(-14, 0)]
    atr = sum(trs) / 14
    e20, e50 = ema(list(cl), 20), ema(list(cl), 50)
    r = rsi(list(cl))
    volx = vo[-1] / (sum(vo[-21:-1]) / 20)
    chg = (c / cl[-2] - 1) * 100
    hh20, ll20 = max(hi[-21:-1]), min(lo[-21:-1])
    side, setups = None, []
    if c > hh20: setups.append("20d-high breakout")
    if c < ll20: setups.append("20d-low breakdown")
    up = c > e20 > e50
    dn = c < e20 < e50
    if up and c > hh20 and volx >= 1.3 and 55 <= r <= 75: side = "CALL"
    elif dn and c < ll20 and volx >= 1.3 and 25 <= r <= 45: side = "PUT"
    if not side:
        return None
    score = volx * min(abs(chg), 4) * (1 if 1.0 <= atr / c * 100 <= 4 else 0.5)
    stop = round(c - 1.0 * atr, 2) if side == "CALL" else round(c + 1.0 * atr, 2)
    tgt = round(c + 2.0 * atr, 2) if side == "CALL" else round(c - 2.0 * atr, 2)
    return dict(sym=sym, side=side, close=round(c, 2), chg=round(chg, 2), rsi=round(r, 1),
                volx=round(volx, 2), atr_pct=round(atr / c * 100, 2), stop=stop, target=tgt,
                setups=", ".join(setups), score=round(score, 2))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--show", type=int, default=10)
    a = ap.parse_args()
    hits, failed = [], []
    for s in FNO:
        rows = fetch(s)
        if rows is None:
            failed.append(s); continue
        h = analyse(s, rows)
        if h: hits.append(h)
        time.sleep(0.25)
    if len(failed) == len(FNO):
        raise SystemExit("No data: could not reach Yahoo Finance (network blocked?).")
    hits.sort(key=lambda h: -h["score"])
    print("Scanned %d, failed %d, setups %d" % (len(FNO) - len(failed), len(failed), len(hits)))
    print("%-12s %-4s %9s %6s %5s %5s %5s %9s %9s  %s" % (
        "SYMBOL", "SIDE", "CLOSE", "CHG%", "RSI", "VOLx", "ATR%", "STOP", "TARGET", "SETUP"))
    for h in hits[:a.show]:
        print("%-12s %-4s %9.2f %6.2f %5.1f %5.2f %5.2f %9.2f %9.2f  %s" % (
            h["sym"], h["side"], h["close"], h["chg"], h["rsi"], h["volx"], h["atr_pct"],
            h["stop"], h["target"], h["setups"]))
    json.dump(hits, open("nse_scan_results.json", "w"), indent=1)


if __name__ == "__main__":
    import urllib.parse
    main()

#!/usr/bin/env python3
"""Pick at most ONE next-day CALL from NSE F&O stocks, using the setup that tested best.

Setup (tested on 2 years, ~90 F&O stocks, both years separately):
  uptrend (close > EMA50 and EMA20 > EMA50), RSI(2) < 10, and close in the bottom 25% of
  the day's range (IBS < 0.25). Buy an ATM CALL ~30 days to expiry at next open, sell at
  close of day 2. Simulated option result: ~46% win rate, avg +3% per trade, profitable in
  both test years. Every option-buying strategy tested won about 50% or less.
Usage: python3 nse_best.py   (best run after 3:30 PM IST)
"""
import json, time, urllib.request, urllib.parse
from nse_scan import FNO, UA


def ema_s(x, n):
    k, out = 2 / (n + 1), [x[0]]
    for v in x[1:]: out.append(v * k + out[-1] * (1 - k))
    return out


def rsi_s(c, n):
    out, g, l = [50] * len(c), 0, 0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]; up, dn = max(d, 0), max(-d, 0)
        if i <= n: g += up / n; l += dn / n
        else: g = (g * (n - 1) + up) / n; l = (l * (n - 1) + dn) / n
        if i >= n: out[i] = 100 if l == 0 else 100 - 100 / (1 + g / l)
    return out


def get(s):
    url = "https://query2.finance.yahoo.com/v8/finance/chart/%s.NS?range=2y&interval=1d" % urllib.parse.quote(s)
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            return [x for x in zip(q["open"], q["high"], q["low"], q["close"], q["volume"]) if None not in x]
        except Exception:
            time.sleep(5)


def main():
    cands = []
    for s in FNO:
        rows = get(s); time.sleep(1)
        if not rows or len(rows) < 150: continue
        O, H, L, C, V = zip(*rows)
        e20, e50, r2 = ema_s(C, 20), ema_s(C, 50), rsi_s(C, 2)
        ibs = lambda j: (C[j] - L[j]) / (H[j] - L[j]) if H[j] > L[j] else 0.5
        sig = lambda j: C[j] > e50[j] and e20[j] > e50[j] and r2[j] < 10 and ibs(j) < 0.25
        i = len(C) - 1
        if not sig(i): continue
        past = [j for j in range(60, len(C) - 3) if sig(j)]
        wins = sum(C[j + 2] > O[j + 1] for j in past)
        atr = sum(max(H[j] - L[j], abs(H[j] - C[j - 1]), abs(L[j] - C[j - 1])) for j in range(i - 13, i + 1)) / 14
        turn = C[i] * sum(V[i - 20:i]) / 20 / 1e7
        if len(past) < 3 or turn < 100: continue          # need history and liquidity
        cands.append(dict(sym=s, close=C[i], rsi2=r2[i], atr=atr, wins=wins, n=len(past),
                          rate=wins / len(past), turn=turn))
    if not cands:
        print("NO TRADE: no liquid stock matches the tested setup today."); return
    cands.sort(key=lambda c: (-c["rate"], -c["n"]))
    for c in cands:
        print("%-11s close %.2f  RSI2 %.1f  ATR %.2f  own history %d/%d up (%.0f%%)  turnover %.0f Cr" % (
            c["sym"], c["close"], c["rsi2"], c["atr"], c["wins"], c["n"], 100 * c["rate"], c["turn"]))
    b = cands[0]
    print("\nBEST 1: %s ATM CALL, ~30 days to expiry | buy at next open | sell at close of day 2 | emergency stop (stock) %.2f"
          % (b["sym"], b["close"] - 1.5 * b["atr"]))


if __name__ == "__main__":
    main()

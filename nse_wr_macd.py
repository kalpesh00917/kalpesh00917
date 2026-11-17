#!/usr/bin/env python3
"""Scan NSE F&O stocks: weekly Williams %R(200) > -20, weekly MACD(24,52,14,EMA) line > signal and > 0,
and a daily breakout today (close above the highest high of the previous N sessions).
Weekly bars are built from daily bars. A scan lists matches; it does not predict anything.
"""
import json, sys, time, datetime, urllib.request, urllib.parse
from nse_scan import FNO, UA

EXTRA = """ABCAPITAL ALKEM ANGELONE APLAPOLLO ASHOKLEY ASTRAL ATGL BANKINDIA BDL BHARATFORG BIOCON BLUESTARCO
BOSCHLTD BSE CAMS CDSL CESC CGPOWER CHAMBLFERT COLPAL CONCOR CROMPTON CUMMINSIND CYIENT DALBHARAT DELHIVERY
EXIDEIND FORTIS GLENMARK GMRAIRPORT GODREJPROP GRANULES HFCL HUDCO ICICIGI ICICIPRULI IDEA IEX IGL INDHOTEL
INDIANB INDUSTOWER INOXWIND IREDA IRFC JINDALSTEL JSWENERGY JUBLFOOD KALYANKJIL KEI KPITTECH LAURUSLABS
LICHSGFIN LICI LODHA LTF MANAPPURAM MANKIND MARICO MAXHEALTH MAZDOCK MCX MFSL MOTHERSON MUTHOOTFIN NATIONALUM
NAUKRI NBCC NCC NHPC NYKAA OBEROIRLTY OFSS OIL PAGEIND PATANJALI PAYTM PETRONET PHOENIXLTD PIIND PNBHOUSING
POLICYBZR POONAWALLA PPLPHARMA PRESTIGE RBLBANK RVNL SBICARD SHREECEM SOLARINDS SONACOMS SRF SUPREMEIND SUZLON
SYNGENE TATACHEM TATAELXSI TATATECH TIINDIA TORNTPHARM TORNTPOWER UNIONBANK UNITDSPR UNOMINDA UPL VOLTAS
YESBANK WELCORP ADANIENSOL ADANIGREEN AMBER BAJAJHLDNG HINDPETRO HINDZINC IIFL M&MFIN VBL TITAGARH
HDFCAMC SWIGGY HYUNDAI WAAREEENER PREMIERENE NUVAMA KAYNES FORCEMOT POWERINDIA ENRIN""".split()
SYMS = list(dict.fromkeys(FNO + EXTRA))
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def ema(x, n):
    k, o = 2 / (n + 1), [x[0]]
    for v in x[1:]: o.append(v * k + o[-1] * (1 - k))
    return o


def get(s):
    url = "https://query2.finance.yahoo.com/v8/finance/chart/%s.NS?range=6y&interval=1d" % urllib.parse.quote(s)
    for a in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            return [(datetime.datetime.fromtimestamp(t, IST).date(), h, l, c, v)
                    for t, h, l, c, v in zip(r["timestamp"], q["high"], q["low"], q["close"], q["volume"])
                    if None not in (h, l, c, v)]
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(6 * (a + 1))
        except Exception:
            time.sleep(4)


def weekly(rows):
    wk = {}
    for d, h, l, c, v in rows:
        k = d.isocalendar()[:2]
        w = wk.setdefault(k, [h, l, c]); w[0] = max(w[0], h); w[1] = min(w[1], l); w[2] = c
    return [wk[k] for k in sorted(wk)]


def main():
    hits, nodata, checked = [], [], 0
    for s in SYMS:
        rows = get(s); time.sleep(0.8)
        if not rows or len(rows) < 300: nodata.append(s); continue
        checked += 1
        W = weekly(rows)
        if len(W) < 215: nodata.append(s); continue
        wh, wl, wc = zip(*W)
        hh, ll = max(wh[-200:]), min(wl[-200:])
        wr = (hh - wc[-1]) / (hh - ll) * -100 if hh > ll else -50
        m = [a - b for a, b in zip(ema(wc, 24), ema(wc, 52))]
        sg = ema(m, 14)
        if not (wr > -20 and m[-1] > sg[-1] and m[-1] > 0): continue
        D = rows; c = D[-1][3]
        hi20 = max(r[1] for r in D[-21:-1]); hi50 = max(r[1] for r in D[-51:-1])
        vx = D[-1][4] / (sum(r[4] for r in D[-21:-1]) / 20)
        chg = (c / D[-2][3] - 1) * 100
        b20, b50 = c > hi20, c > hi50
        hits.append(dict(sym=s, date=str(D[-1][0]), close=round(c, 2), chg=round(chg, 2), wr=round(wr, 1),
                         macd=round(m[-1], 2), sig=round(sg[-1], 2), hi20=round(hi20, 2), hi50=round(hi50, 2),
                         b20=b20, b50=b50, volx=round(vx, 2)))
    json.dump(hits, open("nse_wr_macd_results.json", "w"), indent=1)
    print("checked %d, no data %d, pass weekly filters %d" % (checked, len(nodata), len(hits)))
    print("last daily bar:", max(h["date"] for h in hits) if hits else "-")
    print("\nWEEKLY OK + DAILY BREAKOUT TODAY (close > prior 20-day high):")
    print("%-11s %9s %6s %7s %5s %9s %9s %5s  %s" % ("SYMBOL", "CLOSE", "CHG%", "WR200", "VOLx", "20D-HIGH", "50D-HIGH", "", "also 50d"))
    for h in sorted([h for h in hits if h["b20"]], key=lambda h: -h["volx"]):
        print("%-11s %9.2f %6.2f %7.1f %5.2f %9.2f %9.2f       %s" % (h["sym"], h["close"], h["chg"], h["wr"], h["volx"], h["hi20"], h["hi50"], "YES" if h["b50"] else "no"))
    print("\nWEEKLY OK but NO breakout today (within 2% of 20-day high):")
    for h in hits:
        if not h["b20"] and h["close"] >= h["hi20"] * 0.98:
            print("%-11s %9.2f %6.2f  20D-high %.2f" % (h["sym"], h["close"], h["chg"], h["hi20"]))
    print("\nno data:", " ".join(nodata))


if __name__ == "__main__":
    main()

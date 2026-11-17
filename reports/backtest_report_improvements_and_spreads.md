# Backtest report: improving the strategy, and bull call spreads (NSE F&O stocks)

Date: 18 Nov 2026. Data: Yahoo Finance daily bars, about 6 years per stock, 199 stocks.
**For information only. Not investment advice.** Follows `backtest_report_wr_macd_breakout.md`.

## 1. Verdict
- **Stock trades:** a dip-in-uptrend entry with a stop-loss gives a high win rate (up to about 75%) and a
  10-14% worst drawdown, but the average profit is tiny (+0.05R to +0.08R per trade) and the first year was flat.
  Not proven to be a real edge.
- **Bull call spreads did not help.** They lost more than plain calls in every test. No option structure tested
  here made money after costs.

## 2. Part A: entry and exit improvements (stock trades)
**Test period:** 5 Dec 2024 to 6 Nov 2026, split in half at 27 Nov 2025.
**Rules:** entry at the signal day's close, maximum hold 5 days, stop checked first if both stop and target
are hit the same day, one trade per day (lowest RSI-2), 1% of equity risked per trade, compounding.
Costs are not included. R is the amount risked per trade; ATR is the 14-day average true range.

Entries tested:
1. **breakout**: your strategy (weekly %R(200) > -20, weekly MACD(24,52,14) above signal and 0, daily 20-day breakout)
2. **dip in weekly uptrend**: same weekly filters, RSI-2 < 10
3. **dip + weak close, weekly uptrend**: as 2, plus close in the bottom 25% of the day's range
4. **dip + weak close, uptrend only**: close > 50-day average, 20-day > 50-day, RSI-2 < 10, bottom-25% close (no weekly filters)

| Entry | Target / Stop (ATR) | Trades | Win rate | Avg R | Return | Max drawdown | 1st half avg R | 2nd half avg R |
|---|---|---|---|---|---|---|---|---|
| breakout | 0.5 / 1.5 | 377 | 67.6% | -0.049 | -17.4% | -21.9% | -0.021 | -0.077 |
| breakout | 2.0 / 1.0 | 377 | 43.5% | +0.033 | +10.3% | -32.1% | +0.166 | -0.100 |
| dip, weekly uptrend | 1.0 / 1.5 | 348 | 55.7% | +0.010 | +2.6% | -13.7% | -0.035 | +0.052 |
| dip + weak close, weekly uptrend | 1.0 / 1.5 | 271 | 57.9% | +0.019 | +4.5% | -9.6% | -0.031 | +0.066 |
| dip + weak close, uptrend only | **0.5 / 1.5** | 306 | **74.8%** | +0.047 | +14.9% | **-10.1%** | +0.006 | +0.089 |
| dip + weak close, uptrend only | **1.0 / 1.5** | 306 | **59.8%** | +0.064 | +20.8% | -13.3% | -0.005 | +0.137 |
| dip + weak close, uptrend only | 1.5 / 1.5 | 306 | 54.2% | +0.071 | +23.1% | -13.6% | +0.007 | +0.138 |
| dip + weak close, uptrend only | 2.0 / 1.0 | 306 | 45.4% | +0.080 | +25.1% | -20.7% | -0.047 | +0.213 |
| dip + weak close, uptrend only | 3.0 / 1.0 | 306 | 43.5% | +0.027 | +6.4% | -24.6% | -0.094 | +0.155 |

(Only a selection of the 20 combinations tested is shown. All are in the script output.)

### Findings
1. **A dip entry beats a breakout entry.** The breakout entry lost money in the second half.
2. **The weekly %R and MACD filters made results worse,** not better.
3. **Win rate and payoff trade off.** A 75% win rate came from a small target (0.5 ATR) and a wide stop (1.5 ATR),
   which makes each win small and each loss large.
4. **Drawdown was lowest, about 10%, with the small-target, wide-stop setups.**
5. **The edge is too small to trust.** Average +0.05R to +0.08R over 306 trades is within normal chance
   (standard error about 0.06R). The first half was about zero.

## 3. Part B: bull call spread vs plain call (simulated options)
**Structure:** buy an at-the-money call, sell a higher call 0.5 or 1.0 standard deviations away (30-day volatility),
30 days to expiry. Exit after 3 or 5 days. Return is % of the money paid (the net debit).
**Pricing:** Black-Scholes, volatility = 20-day realised volatility x 1.15 (minimum 15%), 6.5% interest, same
volatility on both strikes (no skew), 1.5% cost on every leg at entry and at exit.
**Portfolio:** one trade per day, 1% of equity per trade, 5 Dec 2024 to 6 Nov 2026.

| Signal | Structure | Hold | Trades | Win rate | Avg | Median | Max drawdown | 1st half avg | 2nd half avg |
|---|---|---|---|---|---|---|---|---|---|
| Dip in uptrend | Plain call | 3d | 1,184 | 43.9% | -1.0% | -5.3% | -13.7% | -3.6% | +2.3% |
| Dip in uptrend | Plain call | 5d | 1,184 | 40.3% | -1.8% | -11.3% | -19.9% | -3.2% | 0.0% |
| Dip in uptrend | Spread 0.5 sd | 3d | 1,184 | 39.7% | -7.4% | -6.9% | -24.0% | -9.1% | -5.1% |
| Dip in uptrend | Spread 0.5 sd | 5d | 1,184 | 40.4% | -7.6% | -8.1% | -26.0% | -8.8% | -5.9% |
| Dip in uptrend | Spread 1.0 sd | 3d | 1,184 | 44.6% | -3.0% | -3.8% | -15.4% | -5.1% | -0.1% |
| Dip in uptrend | Spread 1.0 sd | 5d | 1,184 | 42.3% | -3.4% | -7.1% | -20.2% | -4.9% | -1.4% |
| Your strategy | Plain call | 3d | 1,714 | 38.3% | -4.5% | -11.0% | -21.1% | -2.4% | -6.5% |
| Your strategy | Plain call | 5d | 1,714 | 37.6% | -4.7% | -14.8% | -21.1% | -2.2% | -7.0% |
| Your strategy | Spread 0.5 sd | 3d | 1,714 | 33.3% | -10.0% | -10.9% | -35.5% | -8.2% | -11.7% |
| Your strategy | Spread 0.5 sd | 5d | 1,714 | 37.7% | -9.6% | -10.8% | -34.7% | -7.8% | -11.2% |
| Your strategy | Spread 1.0 sd | 3d | 1,714 | 39.7% | -6.0% | -8.7% | -25.8% | -3.9% | -7.9% |
| Your strategy | Spread 1.0 sd | 5d | 1,714 | 40.3% | -5.8% | -10.0% | -25.3% | -3.7% | -7.8% |

"Trades" counts every signal. The worst single trade was a 100% loss of the money paid in every row.

### Findings
1. **Spreads lost more than plain calls** in all 12 rows, and had deeper drawdowns.
2. **The sold call caps profit, and two legs cost twice as much to trade.** The stocks moved only a little in 3-5 days.
3. **Correction to an earlier claim:** an earlier 30-stock test showed about +3% per trade for the dip rule with options.
   On this larger test (199 stocks, entry at the signal close) it averages about -1% to -2%. The earlier figure was
   too optimistic and did not hold up.

## 4. Conclusions
1. No option structure tested (plain call, bull call spread) made money after costs.
2. A stock-level dip strategy with a stop-loss shows high win rates and about 10-14% drawdown, but the
   average profit is too small to be proven.
3. If trading at all: use delivery stocks, a stop-loss, 0.5-1% risk per trade, and paper-trade 30-50 trades first.
4. A monthly SIP in an index fund remains the most reliable way to grow small capital.

## 5. Limits of this test
- About 2 years of testable data in one market regime (a strong market in 2025-26).
- Options are modelled, not real quotes. No volatility skew, no real bid-ask spreads, no margin or tax.
- Part A excludes trading costs, which could remove most of a +0.05R edge.
- Entries at the signal day's close, not the next open.
- Stock list of 199 is approximate, not NSE's official F&O list.
- Many variants were tried (multiple-testing). The best-looking result is the most likely to be luck.
- Past results do not predict future results.

## 6. Files
- `reports/backtest_improvements_stop_target.py`: Part A
- `reports/backtest_bull_call_spread.py`: Part B
- `reports/backtest_wr_macd_breakout.py`: the original strategy test

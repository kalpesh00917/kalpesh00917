# Backtest report: Weekly %R + Weekly MACD + Daily Breakout (NSE F&O stocks)

Date of report: 18 Nov 2026. Data: Yahoo Finance daily bars, about 6 years per stock.
**For information only. Not investment advice.**

## 1. Verdict
**No usable edge for buying calls.** The strategy wins about as often as picking a stock at random, and
the simulated option trade **loses money on average in both halves of the test**.

## 2. Strategy tested (settings from the TradingView screenshots)
| Part | Rule |
|---|---|
| Weekly Williams %R | Length 200, value **above -20** |
| Weekly MACD | Fast 24, slow 52, signal 14, EMA. MACD line **above signal** and **above 0** |
| Daily trigger | Close **above the highest high of the previous 20 sessions** |
| Entry | At the close of the signal day |
| Exits tested | After 1, 3, 5 and 10 trading days (no stop-loss, no target) |

The weekly values use the still-forming current week, the same as the TradingView chart.

## 3. Data and method
- 199 NSE F&O stocks, about 6 years of daily bars. Weekly bars were built from daily bars.
- The weekly indicators need about 4 years of warm-up, so the **test period is 5 Dec 2024 to 2 Nov 2026**.
- The period was split in half at 18 Nov 2025 to check whether results hold in both halves.
- Four groups compared: every day (baseline), 20-day breakout only, weekly filters only, and the full strategy.
- Options are **simulated**: at-the-money call, 30 days to expiry, Black-Scholes price with volatility
  from the stock's last 20 days times 1.15, a 6.5% interest rate, and 1.5% cost on buying and on selling.

## 4. Results: the stock's move after the signal
"Closed higher" is the share of trades where the stock was up after the holding period.

| Group | Hold | Trades | Closed higher | Average move |
|---|---|---|---|---|
| Every day (baseline) | 5 days | 89,446 | 48.4% | +0.06% |
| 20-day breakout only | 5 days | 5,035 | 48.5% | +0.05% |
| Weekly filters only | 5 days | 16,456 | 49.5% | 0.00% |
| **Full strategy** | 1 day | 1,679 | 47.2% | -0.06% |
| **Full strategy** | 3 days | 1,679 | 48.4% | -0.05% |
| **Full strategy** | 5 days | 1,679 | 50.3% | +0.07% |
| **Full strategy** | 10 days | 1,679 | 49.8% | +0.14% |

## 5. Consistency: first half vs second half (full strategy)
| Hold | 1st half: closed higher / average | 2nd half: closed higher / average |
|---|---|---|
| 1 day | 48.7% / +0.05% | 45.9% / -0.17% |
| 3 days | 50.7% / +0.20% | 46.4% / -0.28% |
| 5 days | 51.8% / +0.27% | 49.0% / -0.12% |
| 10 days | 52.1% / +0.48% | 47.7% / -0.17% |

The small gain in the first half **disappeared in the second half**.

## 6. Results: simulated option buyer (ATM call, 30 days to expiry)
| Group | Hold | Win rate | Average | Median | 1st half avg | 2nd half avg |
|---|---|---|---|---|---|---|
| 20-day breakout only | 3 days | 37.7% | -5.4% | -11.3% | -4.4% | -6.5% |
| 20-day breakout only | 5 days | 35.5% | -7.8% | -17.2% | -8.1% | -7.6% |
| **Full strategy** | 3 days | **37.7%** | **-5.5%** | -11.4% | -2.4% | -8.3% |
| **Full strategy** | 5 days | **36.9%** | **-5.7%** | -15.1% | -2.4% | -8.7% |

## 7. Conclusions
1. The weekly filters did not improve on the plain breakout.
2. The stock closes higher about half the time, no better than the baseline.
3. The option buyer wins about 37% of trades and loses about 5-6% per trade on average, in both halves.
4. **Do not buy calls on this signal.**

## 8. Limits of this test
- Only about 2 years of testable signals, one market regime (a strong market in 2025-26).
- Option prices are modelled, not real. Real spreads, volatility changes and liquidity could make results worse or better.
- Entry at the close of the signal day, not the next open.
- Stock list of 199 is approximate, not NSE's official F&O list. About 19 symbols had no data.
- No stop-loss or target was tested, and no trading costs or taxes beyond the 1.5% option cost.
- Past results do not predict future results.

## 9. Files
- `reports/backtest_wr_macd_breakout.py`: the backtest script (needs the cached daily data folder `c6/`).
- `nse_wr_macd.py`: the live scanner for the same conditions.

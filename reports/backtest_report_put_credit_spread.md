# Backtest report: bull put credit spread (NSE F&O stocks)

Date: 18 Nov 2026. Data: Yahoo Finance daily bars, about 6 years per stock, 199 stocks.
**For information only. Not investment advice.** Follows the two earlier reports in this folder.

## 1. Verdict
The put credit spread gives a **high win rate (74-88%)** but **about zero average profit** after costs, with
**5-17% drawdowns** and **4-14% of trades losing the full risk**. Not a proven edge.

## 2. Strategy tested
| Part | Rule |
|---|---|
| Structure | **Sell** a put below the stock price, **buy** a cheaper put 0.5 standard deviations (sd) lower. Collect a credit. |
| Sold put strike | 0.5 sd below, or 1.0 sd below, the signal-day close (sd = 30-day volatility move) |
| Expiry | 30 days |
| Exit | After 5 trading days (cost to close at the modelled price), or held to expiry |
| Max risk | Width of the spread minus the credit |
| Signals | (1) any uptrend day; (2) dip in uptrend; (3) your weekly %R + MACD + 20-day breakout strategy |

Signal definitions:
- **Uptrend:** close above the 50-day average and the 20-day average above the 50-day.
- **Dip in uptrend:** uptrend, RSI-2 below 10, and a close in the bottom 25% of the day's range.
- **Your strategy:** weekly Williams %R(200) above -20, weekly MACD(24,52,14) above signal and above 0, and a daily close above the previous 20-day high.

## 3. Data and method
- 199 stocks; weekly bars built from daily bars; weekly indicators need a long warm-up.
- **Test period:** 5 Dec 2024 to 14 Oct 2026, split in half at 10 Nov 2025 to check consistency.
- **Option pricing:** Black-Scholes puts, volatility = 20-day realised volatility x 1.15 (minimum 15%),
  6.5% interest, same volatility on both strikes (no skew), 1.5% cost on every leg at entry and on a 5-day exit.
- Trades with a credit under 0.2% of the stock price or over 95% of the width were skipped.
- **Portfolio:** one trade per day (lowest RSI-2), 1% of equity at maximum loss per trade, compounding.
  Trades are treated one after another, so overlapping positions are **not** modelled.
- Return is % of maximum risk.

## 4. Results
| Signal | Sold put | Exit | Trades | Win rate | Avg return | Worst trade | Full-loss trades | Portfolio return | Max drawdown | 1st half avg | 2nd half avg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Any uptrend day | 0.5 sd | 5 days | 34,393 | 54.0% | -2.3% | -151% | 0.1% | -9.1% | -9.9% | -2.1% | -2.4% |
| Any uptrend day | 0.5 sd | Expiry | 34,393 | 73.9% | -0.6% | -100% | 14.1% | +10.7% | -14.3% | +2.1% | -3.5% |
| Any uptrend day | 1.0 sd | 5 days | 32,468 | 62.7% | -0.6% | -135% | 0.0% | -4.9% | -5.9% | -0.5% | -0.7% |
| Any uptrend day | 1.0 sd | Expiry | 32,468 | 87.0% | -0.2% | -100% | 5.3% | +4.2% | -5.4% | +0.8% | -1.2% |
| Dip in uptrend | 0.5 sd | 5 days | 1,176 | 59.9% | -1.0% | -136% | 0.3% | -6.6% | -8.7% | -2.3% | +0.4% |
| Dip in uptrend | 0.5 sd | Expiry | 1,176 | 73.8% | -0.2% | -100% | 12.8% | -2.5% | -17.5% | -3.3% | +3.3% |
| Dip in uptrend | 1.0 sd | 5 days | 1,108 | 68.3% | -0.1% | -129% | 0.3% | -2.9% | -4.3% | -0.7% | +0.5% |
| Dip in uptrend | 1.0 sd | Expiry | 1,108 | **88.0%** | **+1.0%** | -100% | 4.6% | -0.7% | -7.8% | -1.8% | +4.1% |
| Your strategy | 0.5 sd | 5 days | 1,652 | 55.4% | -1.5% | -119% | 0.1% | -7.6% | -8.5% | -0.1% | -2.7% |
| Your strategy | 0.5 sd | Expiry | 1,652 | 73.8% | -0.7% | -100% | 14.1% | +14.2% | -16.0% | +5.4% | -6.1% |
| Your strategy | 1.0 sd | 5 days | 1,588 | 64.4% | -0.3% | -114% | 0.1% | -2.6% | -3.7% | +0.5% | -0.9% |
| Your strategy | 1.0 sd | Expiry | 1,588 | 87.5% | -0.2% | -100% | 5.9% | +5.2% | -9.4% | +3.8% | -3.6% |

"Trades" counts every signal. A worst trade below -100% means the closing cost at 5 days exceeded the maximum risk
because of modelled costs. Portfolio return and drawdown use one trade per day.

## 5. Findings
1. **High win rate, near-zero profit.** A winner earns only the small credit, and a loser costs the spread's
   width minus the credit. About 4-6% of 1.0 sd trades and 13-14% of 0.5 sd trades lost the full risk.
2. **Sold put farther away (1.0 sd) has a higher win rate (87-88%) and smaller drawdowns (5-9%)** than 0.5 sd
   (74%, 14-17%), but the average return is about the same, near zero.
3. **Early exit after 5 days did worse** than holding to expiry in every row.
4. **Results were inconsistent between halves** for most rows. The best row (dip signal, 1.0 sd, expiry,
   +1.0% average) was -1.8% in the first half and +4.1% in the second, so it cannot be called reliable.
5. **The signals add little.** The "any uptrend day" baseline performs about as well as the signal-based entries.

## 6. Limits of this test
- Options are modelled, not real quotes. Real Indian put skew, bid-ask spreads and liquidity are not included.
- Overlapping open positions are ignored, so real drawdowns (especially when held to expiry) would be larger.
- Margin, lot sizes, brokerage and taxes are not included. Stock option lots in India are large.
- About 2 years of data in a mostly rising market, which favours put sellers. A sharp market fall is not well represented.
- Several variants were tried; the best-looking row is the most likely to be luck.
- Stock list of 199 is approximate, not NSE's official F&O list.
- Past results do not predict future results.

## 7. Overall conclusions across all three reports
| Approach | Result |
|---|---|
| Naked calls on breakouts (incl. weekly %R + MACD) | Lose money (about -4% to -8% per trade) |
| Naked calls on dips | About -1% to -2% per trade on the larger test |
| Bull call spreads | Lose more than plain calls |
| Put credit spreads | High win rate (74-88%), about zero profit, large rare losses |
| Stock dip entry with stop-loss | Tiny, unproven edge (+0.05R to +0.08R) |

No tested approach showed a reliable profit after costs. A monthly index-fund SIP remains the most dependable way to grow small capital.

## 8. Files
- `reports/backtest_put_credit_spread.py`: this test
- `reports/backtest_bull_call_spread.py`, `reports/backtest_improvements_stop_target.py`, `reports/backtest_wr_macd_breakout.py`: earlier tests

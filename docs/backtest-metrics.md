# Backtest Metrics Documentation

This document describes the statistical metrics used in FilterBets backtesting engine.

## Core Metrics

### Win Rate
The percentage of winning bets out of total evaluated bets.

```
Win Rate = (Wins / (Wins + Losses)) × 100
```

- **Range**: 0-100%
- **Interpretation**: Higher is better, but depends on odds

### Return on Investment (ROI)
The net profit as a percentage of total staked amount.

```
ROI = (Total Profit / Total Staked) × 100
```

- **Positive**: Profitable strategy
- **Negative**: Unprofitable strategy
- **Breakeven**: ~0%

### Total Profit/Loss
The absolute profit in stake units.

```
Profit = Sum of (stake × odds - stake) for wins - Sum of stakes for losses
```

---

## Advanced Metrics

### Kelly Criterion

The Kelly Criterion determines the optimal stake size to maximize long-term growth.

**Formula:**
```
Kelly % = W - (1-W)/Odds
```

Where:
- `W` = Win probability (win rate as decimal)
- `Odds` = Decimal odds

**Variants:**
| Variant | Fraction | Risk Level |
|---------|----------|------------|
| Full Kelly | 1.0 | Highest volatility |
| Half Kelly | 0.5 | Moderate volatility |
| Quarter Kelly | 0.25 | Conservative |

**Interpretation:**
- **Positive Kelly**: Strategy has mathematical edge
- **Negative Kelly**: Strategy is expected to lose
- **Higher Kelly**: Requires larger bankroll to weather variance

### Expected Value (EV)

The average amount expected to win/lose per bet.

**Formula:**
```
EV = (Win Rate × Odds) - 1
```

**Example:**
- 55% win rate at 2.00 odds
- `EV = 0.55 × 2.00 - 1 = 0.10`
- Expected profit: 10% of stake per bet

**Probability of Profit**
Estimated likelihood of being profitable over the sample size.

---

### Confidence Interval

A range within which the true win rate likely falls.

**Formula:**
```
CI = Win Rate ± (Z-score × Standard Error)
```

**Z-scores:**
| Confidence | Z-score |
|------------|---------|
| 90% | 1.645 |
| 95% | 1.96 |
| 99% | 2.576 |

**Interpretation:**
- Wider CI → Less certainty about true win rate
- Narrower CI → More certainty (more data)

---

### Statistical Significance

Tests whether observed results are statistically different from chance.

**P-value interpretation:**
| P-value | Interpretation |
|---------|----------------|
| < 0.01 | Very significant |
| < 0.05 | Significant |
| < 0.10 | Marginal |
| ≥ 0.10 | Not significant |

**Effect Size (Cohen's h):**
| Value | Interpretation |
|-------|----------------|
| 0.2 | Small |
| 0.5 | Medium |
| 0.8 | Large |

---

## Risk Metrics

### Sharpe Ratio

Risk-adjusted return calculation.

**Formula:**
```
Sharpe Ratio = (ROI - Risk-free rate) / ROI Standard Deviation
```

**Interpretation:**
| Value | Rating |
|-------|--------|
| < 0 | Poor |
| 0-1 | Adequate |
| 1-2 | Good |
| > 2 | Excellent |

### Risk of Ruin

Probability of losing entire bankroll with infinite play.

**Formula (simplified):**
```
Risk of Ruin ≈ (1 - Kelly)^Bets
```

---

## Sample Size Guidelines

Minimum bets recommended for statistical validity:

| Win Rate | Min Sample |
|----------|------------|
| 50% | ~400 bets |
| 55% | ~300 bets |
| 60% | ~200 bets |
| 70% | ~100 bets |

**Rule of thumb:** At least 30 bets required for any statistical test.

---

## Putting It All Together

A robust backtest result should show:

1. **Positive Expected Value** - Mathematical edge exists
2. **Significant P-value** - Results not due to luck
3. **Sufficient Sample Size** - At least 30-100 bets
4. **Reasonable Kelly** - Not too aggressive
5. **Positive Sharpe** - Good risk-adjusted returns

### Example Analysis

```
Win Rate: 55% (95% CI: 51%-59%)
Avg Odds: 2.00
EV: 10% per bet
Kelly: 0.30 (30%)
P-value: 0.03 (Significant)
Sample: 200 bets
```

**Interpretation:**
- Strategy wins 55% of bets at even odds
- True win rate likely between 51-59%
- 10% expected profit per bet
- Kelly suggests 15% of bankroll per bet (half Kelly)
- Results are statistically significant (p < 0.05)
- 200 bets is a reasonable sample size

---

## References

- Kelly, J.L. (1956). "A New Interpretation of Information Rate"
- Cover, T.M. & Thomas, J.A. (2006). Elements of Information Theory
- Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences

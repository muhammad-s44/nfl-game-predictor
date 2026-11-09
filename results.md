# Model results

Trained on 1848 regular-season games (2018-2024), tested on 271 games from the 2025 regular season. Ties are excluded.

| Method | Correct | Accuracy |
|---|---|---|
| Always pick home team | 146/271 | 53.9% |
| Logistic regression | 161/271 | 59.4% |
| Vegas favorite (spread_line) | 177/271 | 65.3% |

## Logistic regression coefficients

Features are standardized, so each coefficient is the change in the log-odds of a home win for a one-standard-deviation increase in that feature. Positive = helps the home team.

| Feature | Coefficient |
|---|---|
| pf_last3_diff | +0.354 |
| win_pct_diff | +0.267 |
| pa_last3_diff | -0.106 |
| rest_diff | +0.038 |
| div_game | -0.015 |

Logistic regression accuracy on its own training games: 62.6% (vs 59.4% on 2025).

"""Stage 4: predict home wins with logistic regression and compare baselines.

Train on 2018-2024 regular seasons, test on the 2025 regular season.

Run from the repo root (inside the virtual environment):
    python src/model.py
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from analysis import DATA_PATH, load_games_df
from features import build_features

TRAIN_SEASONS = range(2018, 2025)  # 2018..2024 (range excludes the end)
TEST_SEASON = 2025
RESULTS_PATH = "results.md"

# Difference features only: home_x and away_x are already combined in
# x_diff, and giving the model both would make its coefficients unreadable.
MODEL_FEATURES = [
    "pf_last3_diff", "pa_last3_diff", "win_pct_diff", "rest_diff", "div_game",
]


def prepare_games(features):
    """Regular-season games with a winner and complete features.

    Adds the target column `home_win` (1 if the home team won, else 0).
    """
    games = features[features["game_type"] == "REG"]
    # A tie has no winner, so there is no right answer to score against
    games = games[games["home_score"] != games["away_score"]]
    games = games.dropna(subset=MODEL_FEATURES).copy()
    games["home_win"] = (games["home_score"] > games["away_score"]).astype(int)
    return games


def split_train_test(games):
    """Split by season: the model never sees a test-season game in training.

    Splitting by time (not randomly) mirrors real use: you train on the
    past and predict the future.
    """
    train = games[games["season"].isin(TRAIN_SEASONS)]
    test = games[games["season"] == TEST_SEASON]
    return train, test


def train_model(train):
    """Fit scaling + logistic regression on the training games."""
    # Scaling puts features on the same scale (points vs win %), so the
    # regularization treats them fairly and coefficients are comparable.
    model = make_pipeline(StandardScaler(), LogisticRegression())
    model.fit(train[MODEL_FEATURES], train["home_win"])
    return model


def accuracy(predicted_home_win, actual_home_win):
    """Fraction of games where the prediction matched the result."""
    return (predicted_home_win == actual_home_win).mean()


def home_team_baseline(games):
    """Always predict the home team wins."""
    return pd.Series(1, index=games.index)


def vegas_favorite_baseline(games):
    """Predict the Vegas favorite wins.

    spread_line > 0 means the home team is favored. Pick'em games (0) have
    no favorite, so we fall back to the home team.
    """
    return (games["spread_line"] >= 0).astype(int)


def coefficient_table(model):
    """Return (feature, coefficient) pairs, biggest effect first."""
    coefs = model.named_steps["logisticregression"].coef_[0]
    pairs = list(zip(MODEL_FEATURES, coefs))
    return sorted(pairs, key=lambda p: abs(p[1]), reverse=True)


def results_markdown(rows, coefs, train, test):
    """Build the results table (and coefficient table) as Markdown text."""
    lines = [
        "# Model results",
        "",
        f"Trained on {len(train)} regular-season games "
        f"({min(TRAIN_SEASONS)}-{max(TRAIN_SEASONS)}), "
        f"tested on {len(test)} games from the {TEST_SEASON} regular season. "
        "Ties are excluded.",
        "",
        "| Method | Correct | Accuracy |",
        "|---|---|---|",
    ]
    for name, correct, acc in rows:
        lines.append(f"| {name} | {correct}/{len(test)} | {acc:.1%} |")
    lines += [
        "",
        "## Logistic regression coefficients",
        "",
        "Features are standardized, so each coefficient is the change in the "
        "log-odds of a home win for a one-standard-deviation increase in that "
        "feature. Positive = helps the home team.",
        "",
        "| Feature | Coefficient |",
        "|---|---|",
    ]
    for feature, coef in coefs:
        lines.append(f"| {feature} | {coef:+.3f} |")
    return "\n".join(lines) + "\n"


def main():
    games = prepare_games(build_features(load_games_df(DATA_PATH)))
    train, test = split_train_test(games)
    model = train_model(train)

    actual = test["home_win"]
    predictions = {
        "Always pick home team": home_team_baseline(test),
        "Logistic regression": model.predict(test[MODEL_FEATURES]),
        "Vegas favorite (spread_line)": vegas_favorite_baseline(test),
    }
    rows = []
    for name, predicted in predictions.items():
        correct = int((predicted == actual).sum())
        rows.append((name, correct, accuracy(predicted, actual)))

    train_acc = accuracy(model.predict(train[MODEL_FEATURES]), train["home_win"])
    test_acc = accuracy(predictions["Logistic regression"], actual)
    report = results_markdown(rows, coefficient_table(model), train, test)
    # A big gap between train and test accuracy would signal overfitting
    report += (f"\nLogistic regression accuracy on its own training games: "
               f"{train_acc:.1%} (vs {test_acc:.1%} on {TEST_SEASON}).\n")

    print(report)
    with open(RESULTS_PATH, "w") as f:
        f.write(report)
    print(f"saved {RESULTS_PATH}")


if __name__ == "__main__":
    main()

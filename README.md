# nfl-game-predictor

Predicting NFL game outcomes with Python and nflverse data.

## Setup

Stage 1 (`src/explore.py`) uses only the standard library. Later stages need pandas, scikit-learn and matplotlib, installed in a virtual environment so they don't touch your system Python:

```sh
python3 -m venv .venv            # create the environment (once)
source .venv/bin/activate        # activate it (every new terminal)
pip install -r requirements.txt  # install dependencies (once)
```

Run everything from the repo root:

```sh
python src/explore.py    # Stage 1: plain Python
python src/analysis.py   # Stage 2: pandas
```

Type `deactivate` to leave the environment.

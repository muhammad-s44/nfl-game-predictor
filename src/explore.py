import csv 
def load_games(path):
    with open(path) as f:
        return list(csv.DictReader(f))

games = load_games("data/games.csv")
print(len(games))
print(games[0])


# Interview Questions

Fifteen questions an interviewer might ask about this project, with short answers in my own voice. Practise saying them out loud, and don't memorize the wording.

---

**1. Walk me through the project in 30 seconds.**

I built an NFL game predictor from nflverse data going back to 1999. I started by answering simple questions in plain Python, redid them in pandas, made charts, built features that only use information from before each game, and trained a logistic regression model. On the 2025 season it got 59.4% of games right, compared with 53.9% for always picking the home team and 65.3% for the Vegas favorite.

**2. Why did you do Stage 1 without pandas?**

So I actually understood what pandas does for me. When I write `groupby("home_team").sum()` now, I know it's the same as looping through games and adding into a dict. That made the pandas version easy to check, too: I wrote an assert that both versions give identical answers.

**3. How did you handle ties?**

Explicitly, everywhere. In win percentages I left ties out of the denominator, because a tie isn't a home win or a home loss. In the features, a tie counts as half a win, like NFL standings. In the model I dropped ties, because there's no correct winner to score a prediction against. There are only 16 ties since 1999, but silently counting them as losses would be a bug.

**4. What's data leakage, and how did you prevent it?**

Leakage is when a feature contains information you wouldn't have at prediction time, like a "last 3 games average" that accidentally includes the game you're predicting. The model looks great in testing and is useless in reality. I prevented it with `shift(1)` before every rolling calculation, so each game only sees earlier games.

**5. How do you *know* there's no leakage?**

I wrote a test. It scrambles the scores of every game after a cutoff date, rebuilds the features, and checks that features for games up to that date didn't change at all. If any feature read the future, it would change. I also made sure the test can fail: I deleted `shift(1)` and it failed immediately. A second test recomputes features for 150 random games with a slow, obvious filter and checks they match.

**6. Why logistic regression and not something fancier?**

The output is a yes/no (does the home team win?), and logistic regression gives a probability for exactly that. With only five features and about 1,850 training games, a complex model would mostly overfit. It's also explainable: I can point at each coefficient and say what it does. I'd try gradient boosting next, but only after more features.

**7. Explain logistic regression simply.**

It computes a weighted sum of the features, like a linear regression, and then squashes that score through a sigmoid so it lands between 0 and 1. That's the probability of a home win. Training finds the weights that make those probabilities match past results as closely as possible.

**8. Why did you split by season instead of randomly?**

Because in real life you predict future games from past ones. A random split would let the model train on some 2025 games and test on others from the same weeks, which is a sneaky form of leakage. Training on 2018–2024 and testing on 2025 is the honest version.

**9. Why did you scale the features?**

They're in different units: points, win percentage, days of rest. scikit-learn's logistic regression penalizes large weights by default, and that penalty is only fair if features are on the same scale. I put the scaler in a pipeline so it learns its mean and standard deviation from training data only.

**10. Your model loses to Vegas. Is it a failure?**

No, that's the expected result. The betting line includes injuries, quarterback news, weather and a market of people with money on the line. My model only knows recent scores, win percentage and rest. The meaningful comparison is that it beats the simple home-team baseline. I'm also honest that with 271 test games the margin of error is about ±6 points, so I'd want to test on more seasons.

**11. What's `spread_line`, and what did you have to check?**

It's the point spread. I checked its sign against Super Bowls I knew the favorite for, and in nflverse a positive number means the *home* team is favored, which is the opposite of how sportsbooks print lines. I also confirmed it agrees with the moneylines 98% of the time. If I'd assumed the wrong sign, every "favorite" would have been backwards.

**12. What did you find about home-field advantage?**

It shrank. Home teams won 57.7% of decided, non-neutral games from 1999 to 2014 and 55.1% from 2015 to 2025. In 2020, with empty stadiums, it dropped to 50.4%, basically a coin flip, which suggests crowds are a big part of it. I excluded neutral-site games like Super Bowls, since the "home" team there is home only on paper.

**13. Which feature mattered most?**

Recent scoring difference: the home team's average points over its last three games minus the away team's. Season win percentage difference was second. Rest days and division games barely mattered. Because the features were standardized, I can compare those coefficients directly.

**14. What was the hardest bug or decision?**

Making rolling stats per *team* rather than per home or away side. A team is home some weeks and away others, so I reshaped each game into two rows, one per team, sorted by date, computed the rolling stats, then merged them back. I also had to map relocated teams (St. Louis to LA, San Diego to LA Chargers, Oakland to Las Vegas) so their history didn't restart.

**15. What would you improve next?**

Test on several seasons with walk-forward validation instead of just 2025. Add stronger features, like an Elo rating, quarterback changes, and point differential instead of only points. Try including the spread as a feature to see if my features add anything on top of Vegas. And measure probability quality with log loss or a calibration chart, not just accuracy.

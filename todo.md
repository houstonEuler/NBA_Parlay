~~1. Copy the nba_stats.db to this directory, and run nbastatsupdater.py to get an updated dataset.~~
~~add player name to player game logs~~
~~run dkstream and download ud/pp.json files~~
2. Create functions for nbastatsanalysis.py, which will return the desired stats, and confirm they're working.

    c. Function to get stats from nbastats.db
        i. Calculate the number of greater/equal/less games
        ii. Grab opponent stats from hashtagbasketball.com, fanduel, or https://www.bettingpros.com/nba/defense-vs-position/ (same as fanduel) for comparison.
d. Combine into one dataframe
3. Run dkstream3.py, and grab Underdog and Prizepicks data, for initial test.

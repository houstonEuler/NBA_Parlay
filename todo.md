0. Add function that adds a team name to each player row, by parsing the matchup column for what I assume is the first value.
    a. Is it better to do this in sql?
1. Get opponent stats from hashtagbasketball.com, fanduel, or https://www.bettingpros.com/nba/defense-vs-position/ (same as fanduel) for comparison.
2. Add ratios for last 5/10 games
3. Fix Nic Claxton, Scottie Pippen jr, and other players whose stats are not being recognized.
4. Double-check Gary Trent, might be errors, but this seems odd:
68   30324129            Points           Gary Trent Jr.  -125  19.5   Under     18.5               8.0               53.0            -45.0  0.150943
94   30324129  Pts + Reb + Asts           Gary Trent Jr.  -125  25.5   Under     25.5               8.0               53.0            -45.0  0.150943
109  30324129        Pts + Rebs           Gary Trent Jr.  -125  22.5    Over     22.5               8.0               53.0            -45.0  0.150943

They're each highly correlated with points, so it's not impossible, but it's surprising there isn't any variance.

5. Consider searching for player correlations between pts,reb,ast, as that might offer an edge for these combo stats.

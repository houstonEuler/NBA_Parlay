# NBA_Parlay
Tool to help find potentially favorable parlay bets.

Guide (Windows):
1. On your local machine, create a virtual environment in the NBA_Parlay folder
python -m venv venv

2. Activate the virtual environment
venv\scripts\activate

3. Install the requirements
pip install -r requirements.txt



Planning Notes:
1. Get current lines from DraftKings with dkstream script

2. Get available parlay props with manual upload from Underdog and Prizepicks, saved as ud.json and pp.json

3. For available lines, calculate the following:
a. Player performance and variance for the stat, over the season and other periods (10 games, 5 games?)
b. Opponent stats against, showing how players perform against them. (Note: This needs to adjust for the teams they've played, look for existing stats. This should also adjust for position, find out how that's done.)
c. Which lines are more favorable (Maybe create a basic equation that factors player stats, opponent stats allowed, and variance of each)

4. Question: Which of the following should this do?:
a. Calculate and Filter only for lines that are available on UD or PP
b. Calculate for all lines, and sort the most favorable
c. Both?

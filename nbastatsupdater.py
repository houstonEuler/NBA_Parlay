import nbaapi
import sqlite3
import time
import pandas as pd

#Create connection to database
conn = sqlite3.connect('nba_stats.db')
cursor = conn.cursor()

# Create a table for player information
cursor.execute("""
CREATE TABLE IF NOT EXISTS player_game_logs (
    season_id TEXT,
    player_id TEXT,
    player_name TEXT,    
    game_id TEXT,
    game_date TEXT,
    matchup TEXT,
    wl TEXT,
    min INTEGER,
    fgm INTEGER,
    fga INTEGER,
    fg_pct REAL,
    fg3m INTEGER,
    fg3a INTEGER,
    fg3_pct REAL,
    ftm INTEGER,
    fta INTEGER,
    ft_pct FLOAT,
    oreb INTEGER,
    dreb INTEGER,
    reb INTEGER,
    ast INTEGER,
    stl INTEGER,
    blk INTEGER,
    tov INTEGER,
    pf INTEGER,
    pts INTEGER,
    plus_minus INTEGER  
)
""")


#Establishes the table
conn.commit()

#Sets a delay between requests to avoid overloading the server or getting flagged.
player_request_delay = 10  # Adjust this value as needed

#Gets a list of active players from the nbaapi.py file
active_players = nbaapi.active_players

#For each player in active players, gets the current years (2023) game logs. 
for player in active_players:
    player_game_logs = nbaapi.get_player_game_logs(player['id'],2023)
    #For each row in the game logs, it gets the game_id. 
    for index, row in player_game_logs.iterrows():
        game_id = row['Game_ID']
        player_id = player['id']
        # Check if the game with the same game_id already exists in the database
        cursor.execute("SELECT COUNT(*) FROM player_game_logs WHERE game_id=? AND player_id =?", (game_id,player_id,))
        existing_game_count = cursor.fetchone()[0]
        #If the game_id is not found in the database, it adds the stats from the game to the database
        pts_reb_ast = row['PTS'] + row['REB'] + row['AST']
        pts_reb = row['PTS'] + row['REB']
        pts_ast = row['PTS'] + row['AST']
        ast_reb = row['AST'] + row['REB']
        blk_stl = row['BLK'] + row['STL']
        if existing_game_count == 0:
            cursor.execute("INSERT INTO player_game_logs ('season_id', 'player_id', 'player_name', 'game_id', 'game_date', 'matchup', 'wl', 'min', 'fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts', 'plus_minus', 'pts_reb_ast', 'pts_reb', 'pts_ast', 'ast_reb', 'blk_stl') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (row['SEASON_ID'], row['Player_ID'], player['full_name'], row['Game_ID'], row['GAME_DATE'], row['MATCHUP'], row['WL'], row['MIN'], row['FGM'], row['FGA'], row['FG_PCT'], row['FG3M'], row['FG3A'], row['FG3_PCT'], row['FTM'], row['FTA'], row['FT_PCT'], row['OREB'], row['DREB'], row['REB'], row['AST'], row['STL'], row['BLK'], row['TOV'], row['PF'], row['PTS'], row['PLUS_MINUS'], pts_reb_ast, pts_reb, pts_ast, ast_reb, blk_stl))
            conn.commit()
    #Prints the player_id and player name as it progresses through the list of players
    print(f"Player ID: {player['id']} - {player['full_name']}")
    #Sleeps for a number of seconds defined by the player_request_delay
    time.sleep(player_request_delay)







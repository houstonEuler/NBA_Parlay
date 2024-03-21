import sqlite3

#adds combo data to nba_stats.db
conn = sqlite3.connect('nba_stats.db')
cursor = conn.cursor()


new_columns = [
    "pts_reb_ast INTEGER",
    "pts_reb INTEGER",
    "pts_ast INTEGER",
    "ast_reb INTEGER",
    "blk_stl INTEGER"
]

for column in new_columns:
    cursor.execute(f"ALTER TABLE player_game_logs ADD COLUMN {column}")
conn.commit()
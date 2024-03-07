#This script takes the data from Draftkings, as well as from Underdog and Prizepicks, finds the props that match, and are lower than -120, and prints them, sorted by the highest odds.
#This script should be adapted to include nba stats data in the nba_parlay.py file. 

import sqlite3
import pandas as pd
from ud2 import fetch_ud_data
from pp2 import fetch_pp_data
import nbaapi

conn = sqlite3.connect('combodata.db')

cursor = conn.cursor()

ud_data = fetch_ud_data()
pp_data = fetch_pp_data()

pd.set_option('display.max_rows', 1000)

df = pd.read_sql_query("SELECT * FROM propositions_data", conn)
df2 = pd.read_sql_query("SELECT * FROM current_data", conn)

# After reading df2 from the database or merging it
df['Odds'] = pd.to_numeric(df['Odds'], errors='coerce')
df2['Odds'] = pd.to_numeric(df2['Odds'], errors='coerce')

df['Player_Name'] = df['Player_Name'].str.strip()
df2['Player_Name'] = df2['Player_Name'].str.strip()

conn.close()

df3 = []

df = df.sort_values(by=["Prop","Player_Name","Odds","timestamp"])
df2 = df2.sort_values(by=["Odds","Prop","Player_Name"])

df3 = df[["Event_ID","Prop","Player_Name","Outcome","Odds","Line"]]

df4 = df3.drop_duplicates()
df4 = df4.sort_values(by=["Prop","Player_Name","Line"])

df5 = df3[["Event_ID","Player_Name","Prop","Line"]]
df5 = df5.drop_duplicates()

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)



df2['UD'] = ''
df2['PP'] = ''

ud_df = pd.DataFrame(ud_data)
pp_df = pd.DataFrame(pp_data)

name_mapping = {
                'Cameron Johnson' : 'Cam Johnson',
                'Cameron Thomas' : 'Cam Thomas',
                'Nicolas Claxton' : 'Nic Claxton'
}


for index, row in df2.iterrows():
    # Find matching entries in ud_data and pp_data
    ud_match = ud_df[(ud_df['Player_Name'] == row['Player_Name']) & (ud_df['Prop'] == row['Prop'])]
    pp_match = pp_df[(pp_df['Player_Name'] == row['Player_Name']) & (pp_df['Prop'] == row['Prop'])]

    # Update UD and PP columns if matches are found
    if not ud_match.empty:
        df2.at[index, 'UD'] = ud_match.iloc[0]['Line']
    if not pp_match.empty:
        df2.at[index, 'PP'] = pp_match.iloc[0]['Line']


df6 = pd.DataFrame(columns=df2.columns)
df6['Row_Num'] = range(1, len(df6) + 1)


# Iterate over df2 and insert rows into df6
for index, row in df2.iterrows():
    #Check if either UD or PP columns are not empty
    if (row['UD'] or row['PP']) and row['Odds'] < -120:
    # Find matching lines in df5
        event_id = row['Event_ID']
        player_name = row['Player_Name']
        prop = row['Prop']
        line = row['Line']
        matching_lines = df5[(df5['Event_ID'] == event_id) & (df5['Player_Name'] == player_name) & (df5['Prop'] == prop) & (df5['Line'] != line)]

        # Add new rows for different lines
        new_rows = []
        for _, match_row in matching_lines.iterrows():
            new_row = {col: '' for col in df6.columns}  # Use empty strings instead of None
            new_row['Player_Name'] = player_name  # Keep the player name
            new_row['Line'] = match_row['Line']  # Insert the different line
            new_rows.append(new_row)

        # Concatenate the current row and new rows to df6

        df6 = pd.concat([df6, pd.DataFrame([row.to_dict()]), pd.DataFrame(new_rows)], ignore_index=True)


df6 = df6[['Event_ID','Prop','Player_Name','Odds','Line','Outcome','UD','PP']]

prop_mapping = {
                'Points':'PTS',
                '3-PT Made':'FG3M',
                'Pts + Reb + Asts':'PTS + REB + AST',
                'Pts + Rebs':'PTS + REB',
                'Pts + Asts':'PTS + AST',
                'Ast + Rebs':'AST + REB',
                'Rebounds':'REB',
                'Assists':'AST',
                'Steals':'STL',
                'Blocks':'BLK',
                'Blocks + Steals': 'BLK + STL',
                'Turnovers':'TOV', 
}

def res(row_number):
    if 0 <= row_number < len(df6):
        player_name = df6.at[row_number, 'Player_Name']
        prop_main_script = df6.at[row_number, 'Prop']

        # Map the prop to the nbaapi prop using the dictionary
        prop_nbaapi = prop_mapping.get(prop_main_script)

        if prop_nbaapi:
            result = nbaapi.allprop(player_name, prop_nbaapi)
            return result
        else:
            print(f"Prop '{prop_main_script}' not found in the mapping.")
            return None
    else:
        print("Invalid row number.")
        return None

print(df2)
print(df4)
print(df6)

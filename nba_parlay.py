import pandas as pd
import sqlite3
from ud2 import fetch_ud_data
from pp2 import fetch_pp_data
import nbaapi
import time
import logging
import nbastatsanalysis


#Do I want stats to update first, or should I first get the list of players and update only their stats?
#Not having all player stats would make defensive analysis data incomplete, so it should probably run first.

#Maybe create a separate script, that updates the database with additional analysis, like variance and medians for each prop? (see nbastatsanalysis.py)



#Create connections to databases combodata.db has currently and former props/lines/odds from the DraftKings API, and nba_stats has NBA player stats from the nba_stats API (stored through nbaapi.py)
props_conn = sqlite3.connect('combodata.db')


#Create cursors for databases
props_cursor = props_conn.cursor()


#Use ud.py and pp.py to load the manually-saved json files from their websites (Their T&Cs disallow any scripts from being run on their websites)
#Underdog Data: https://api.underdogfantasy.com/beta/v5/over_under_lines
#Prizepicks Data: https://api.prizepicks.com/projections?league_id=7&per_page=500&state_code=TX&single_stat=true
ud_data = fetch_ud_data()
pp_data = fetch_pp_data()


#Adjust display settings for command shell
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

#Reads tables from the props database
all_prop_data = pd.read_sql_query("SELECT * FROM propositions_data", props_conn)
curr_prop_data = pd.read_sql_query("SELECT * FROM current_data", props_conn)

#Converts the Odds column to a numeric value for analysis
all_prop_data['Odds'] = pd.to_numeric(all_prop_data['Odds'], errors='coerce')
curr_prop_data['Odds'] = pd.to_numeric(curr_prop_data['Odds'], errors='coerce')

#Convert database tables "propositions_data" and "current_data" to pandas dataframes
df = all_prop_data[["Prop","Event_ID","Player_Name","Outcome","Odds","Line","timestamp"]]
df2 = curr_prop_data[["Prop","Event_ID","Player_Name","Outcome","Odds","Line"]]

#close database connection
props_conn.close()

#strips any extra spaces from player names
df.loc[:, 'Player_Name'] = df['Player_Name'].str.strip()
df2.loc[:, 'Player_Name'] = df2['Player_Name'].str.strip()

#creates a new dataframe
df3 = []

#sorts dataframes
df = df.sort_values(by=["Prop","Player_Name","Odds","timestamp"])
df2 = df2.sort_values(by=["Odds","Prop","Player_Name"])

#Creates new dataframe, might be unnecessary
df3 = df[["Event_ID","Prop","Player_Name","Outcome","Odds","Line"]]

#creates another dataframe that removes any duplicates, then sorts that dataframe
df4 = df3.drop_duplicates()
df4 = df4.sort_values(by=["Prop","Player_Name","Line"])

#Creates another dataframe (This is getting really excessive) 
df5 = df3[["Event_ID","Player_Name","Prop","Line"]]
df5 = df5.drop_duplicates()

#Adds new columns to dataframe 2 for Underdog and Prizepicks lines
df2['UD'] = ''
df2['PP'] = ''

#Creates dataframes for those lines from the uploaded data
ud_df = pd.DataFrame(ud_data)
pp_df = pd.DataFrame(pp_data)

#Fixes some names that are different between the dataframes. Might need to add more as they're discovered.
name_mapping = {
                'Cameron Johnson' : 'Cam Johnson',
                'Cameron Thomas' : 'Cam Thomas',
}

#Checks if the current prop database matches the player and prop from underdog and prizepicks. If it's not blank, it adds the line to the df2 dataframe for the respective site.
for index, row in df2.iterrows():
    # Find matching entries in ud_data and pp_data
    ud_match = ud_df[(ud_df['Player_Name'] == row['Player_Name']) & (ud_df['Prop'] == row['Prop'])]
    pp_match = pp_df[(pp_df['Player_Name'] == row['Player_Name']) & (pp_df['Prop'] == row['Prop'])]

    # Update UD and PP columns if matches are found
    if not ud_match.empty:
        df2.at[index, 'UD'] = ud_match.iloc[0]['Line']
    if not pp_match.empty:
        df2.at[index, 'PP'] = pp_match.iloc[0]['Line']

#Creates another dataframe with the same columns as df2
df6 = pd.DataFrame(columns=df2.columns)
df6['Row_Num'] = range(1, len(df6) + 1)


# Iterate over df2 and insert rows into df6
for index, row in df2.iterrows():
    #For each row where UD or PP have odds less than -120
    if (row['UD'] or row['PP']) and row['Odds'] < -120:
        #Match values in database with columns in the dataframe
        event_id = row['Event_ID']
        player_name = row['Player_Name']
        prop = row['Prop']
        line = row['Line']
        #Create a new dataframe from the prop_data table where the event_id, player_name, and prop are the same, but the line is different. This is to show if the line has moved for a player/prop over time.
        matching_lines = df5[(df5['Event_ID'] == event_id) & (df5['Player_Name'] == player_name) & (df5['Prop'] == prop) & (df5['Line'] != line)]

        #Create a empty space for new rows
        new_rows = []
        #Creates new rows that show if lines have changed for a player/prop combination to be combined back into the current_props dataframe
        for _, match_row in matching_lines.iterrows():
            new_row = {col: '' for col in df6.columns}  # Use empty strings instead of None
            new_row['Player_Name'] = player_name  # Keep the player name
            new_row['Line'] = match_row['Line']  # Insert the different line
            new_rows.append(new_row)

        # Concatenate the current row and new rows to df6
        df6 = pd.concat([df6, pd.DataFrame([row.to_dict()]), pd.DataFrame(new_rows)], ignore_index=True)

#Reorders the dataframe columns
df6 = df6[['Event_ID','Prop','Player_Name','Odds','Line','Outcome','UD','PP']]

#Creates a mapping of names for certain columns
prop_mapping = {
                'Points':'PTS',
                '3-PT Made':'FG3M',
                'Pts + Reb + Asts':'PTS_REB_AST',
                'Pts + Rebs':'PTS_REB',
                'Pts + Asts':'PTS_AST',
                'Ast + Rebs':'AST_REB',
                'Rebounds':'REB',
                'Assists':'AST',
                'Steals':'STL',
                'Blocks':'BLK',
                'Blocks + Steals': 'BLK_STL',
                'Turnovers':'TOV', 
}


#This maps the props from the prop_mapping dictionary listed above to the props in the pandas dataframe
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

df6['Over_Performance'] = 0
df6['Under_Performance'] = 0

def calculate_performance(row):
    # Connect to the database
    stats_conn = sqlite3.connect('nba_stats.db')
    stats_cursor = stats_conn.cursor()

    # Fetch player_id from nbastats.db based on player_name
    player_name = row['Player_Name']
    prop = row['Prop']

    # Map the prop to the corresponding value in the prop_mapping dictionary
    mapped_prop = prop_mapping.get(prop)
    if not mapped_prop:
        print(f"Prop '{prop}' not found in the mapping.")
        return None, None, None

    stats_cursor.execute("SELECT player_id FROM player_game_logs WHERE player_name = ?", (player_name,))
    player_id = stats_cursor.fetchone()
    if player_id:
        player_id = player_id[0]  # Extracting player_id from tuple

        # Call functions from nbastatsanalysis.py to calculate performance values
        over_performance = nbastatsanalysis.get_over_performance_for_player(player_id, mapped_prop, row['Line'])
        under_performance = nbastatsanalysis.get_under_performance_for_player(player_id, mapped_prop, row['Line'])
        
        # Convert performance columns to numeric data type
        df6['Over_Performance'] = pd.to_numeric(df6['Over_Performance'], errors='coerce')
        df6['Under_Performance'] = pd.to_numeric(df6['Under_Performance'], errors='coerce')
        
        # Close the connection
        stats_conn.close()

        # Return values
        return len(over_performance), len(under_performance)
    else:
        # Close the connection
        stats_conn.close()

        return None, None, None


df6['Over_Performance'], df6['Under_Performance'] = zip(*df6.apply(calculate_performance, axis=1))

df6['Over_Performance'] = pd.to_numeric(df6['Over_Performance'], errors='coerce')
df6['Under_Performance'] = pd.to_numeric(df6['Under_Performance'], errors='coerce')


df6 = df6[['Event_ID', 'Prop', 'Player_Name', 'Odds', 'Line', 'Outcome', 'UD', 'PP', 'Over_Performance', 'Under_Performance']]

df6['Over_Under Diff'] = df6['Over_Performance'] - df6['Under_Performance']

df6['Ratio'] = df6['Over_Performance']/df6['Under_Performance']

df7 = df6.sort_values(by=['Odds','Prop','Ratio'])

df8 = df6.sort_values(by=['Prop','Odds','Ratio'])

df9 = df6.sort_values(by=['Ratio','Prop','Odds'])

print("DF6---------------------------------------------------------------------------DF6")
print(df6)
print("DF7---------------------------------------------------------------------------DF7")
print(df7)
print("DF8---------------------------------------------------------------------------DF8")
print(df8)
print("DF9---------------------------------------------------------------------------DF9")
print(df9)

'''
#Next Steps

### Need to fix the sort, so the changes in odds are in-line with the data.

### Need to add more recent data for comparison, to avoid situations where someone's playing time has increased recently

### Need to incorporate opponent data





#Incorporate stats:
#####################################################
# Need to update nbastats.db to include player name #
#####################################################
#Retrieve over/under/equal stats for player and prop
for index, row in df6.iterrows():
    player_name = row['Player_Name']
    prop = row['Prop']

    over_performance = nbastatsanalysis.get_over_performance_for_player(player_id, prop, line)
    under_performance = nbastatsanalysis.get_under_performance_for_player(player_id, prop, line)
    equal_performance = nbastatsanalysis.get_equal_performance_for_player(player_id, prop, line)
    
    
    #Create a new dataframe from the prop_data table where the event_id, player_name, and prop are the same, but the line is different. This is to show if the line has moved for a player/prop over time.
    matching_lines = df5[(df5['Event_ID'] == event_id) & (df5['Player_Name'] == player_name) & (df5['Prop'] == prop) & (df5['Line'] != line)]

    #Create a empty space for new rows
    new_rows = []
    #Creates new rows that show if lines have changed for a player/prop combination to be combined back into the current_props dataframe
    for _, match_row in matching_lines.iterrows():
        new_row = {col: '' for col in df6.columns}  # Use empty strings instead of None
        new_row['Player_Name'] = player_name  # Keep the player name
        new_row['Line'] = match_row['Line']  # Insert the different line
        new_rows.append(new_row)

    # Concatenate the current row and new rows to df6
    df6 = pd.concat([df6, pd.DataFrame([row.to_dict()]), pd.DataFrame(new_rows)], ignore_index=True)    

over_performance = nbastatsanalysis.get_over_performance_for_player()
under_performance = nbastatsanalysis.get_under_performance_for_player()
equal_performance = nbastatsanalysis.get_equal_performance_for_player()

#Retrieve average stats for player and prop
mean_performance = nbastatsanalysis.get_mean_variance_for_player()

#Retrieve median stats for player and prop
median_performance = nbastatsanalysis.get_median_variance_for_player()

#Retrieve variance? for player and prop
#Might need to split out variance, or create a better way to view it. A single number is less useful than a few numbers that give a better picture of the distribution.


#Retrieve Opponent Stats and Variance? Can this be from an external source???
opp_performance = nbastatsanalysis.analyze_player_performance_by_matchup()

'''


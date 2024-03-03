import json
import pandas as pd


ud_mapping = {
    'Pts + Rebs + Asts': 'Pts + Reb + Asts',
    '3-Pointers Made': '3-PT Made',
    'Points + Rebounds': 'Pts + Rebs',
    'Points + Assists': 'Pts + Asts',
    'Rebounds + Assists': 'Ast + Rebs'
}

def fetch_ud_data():
    # Assuming json_string contains your JSON data
    with open('ud.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Mapping from appearance id to player id
    appearance_to_player = {}
    for appearance in data['appearances']:
        appearance_to_player[appearance['id']] = appearance['player_id']

    # Mapping from player id to player name
    player_to_name = {}
    for player in data['players']:
        if player['sport_id'] in ['NBA','NBACOMBOS']:
            full_name = f"{player['first_name']} {player['last_name']}"
            player_to_name[player['id']] = full_name

    # Updated data list
    ud_data = []

    # Iterate through the over_under_lines list and add required fields
    for item in data['over_under_lines']:   
        if len(item['options']) < 2:
            continue
        
        player_id = appearance_to_player[item['over_under']['appearance_stat']['appearance_id']]
        if player_id in player_to_name:
            full_name = player_to_name[player_id]
        else:
            continue

        prop_name = item["over_under"]["appearance_stat"]["display_stat"]
        standardized_prop_name = ud_mapping.get(prop_name, prop_name)

        ud_data.append({
            'Player_Name': full_name,
            "Prop": standardized_prop_name,
            "Line": item["stat_value"],
        })
        
    return ud_data

data = fetch_ud_data()
df2 = pd.DataFrame(data)


'''

https://api.underdogfantasy.com/beta/v5/over_under_lines



To-Do - Exclude unrelated stats
Headshots on Maps 1+2
Kills on Maps 1+2
Kills + Assists in Games 1+2
Fantasy Points in Game 1+2
Kills in Game 1+2
Kills in Map 1
Kills in Map 2
Assists on Map 1
Assists on Map 2
Deaths on Map 1
Deaths on Map 2
Deaths on Map 1+2
Games played
Games lost
Games won
Service games lost
Breakpoints won
Sets lost
Double faults
Aces
Shots Attempted
Saves
Goals





Use Regex to recognize Player names and add as a column


exclude_stats = [
    "Headshots on Maps 1+2", "Kills on Maps 1+2", "Kills + Assists in Games 1+2", 
    "Fantasy Points in Game 1+2", "Kills in Game 1+2", "Kills in Map 1", 
    "Kills in Map 2", "Assists on Map 1", "Assists on Map 2", "Deaths on Map 1", 
    "Deaths on Map 2", "Deaths on Map 1+2", "Games played", "Games lost", 
    "Games won", "Service games lost", "Breakpoints won", "Sets lost", 
    "Double faults", "Aces", "Shots Attempted", "Saves", "Goals",
    "Hits Allowed", "Strikeouts","Kills on Map 1+2","Kills in Maps 1+2",
    "Kills in Maps 1+2+3","Fantasy Points in Games 1+2","Kills + Assists in Maps 1+2",
    "Deaths on Maps 1+2","Fantasy Points on Map 2","Fantasy Points on Maps 1+2",
    "Assists on Maps 1+2","Fantasy Points on Map 1","Shots on Target","Goals + Assists",
    "Goals Allowed","Kicking Points","XP Made","Receiving Yards","Rush + Rec TDs",
    "Receptions","Rushing Yards","Pass + Rush Yards","Passing Yards","Power Play Points",
    "FG Made","Shots","Passing TDs","Rush + Rec Yards","Interceptions","Fumbles Lost"
    ]





'''
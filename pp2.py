import json
import pandas as pd

pp_mapping = {
    'Pts+Rebs+Asts': 'Pts + Reb + Asts',
    'Pts+Rebs': 'Pts + Rebs',
    'Pts+Asts': 'Pts + Asts',
    'Rebs+Asts': 'Ast + Rebs',
    'Blocked Shots': 'Blocks',
    'Blks+Stls':'Blocks + Steals'
}


def fetch_pp_data():
    # Load the JSON data
    with open('pp.json', 'r') as file:
        data = json.load(file)

    # Extract the relevant data
    entries = data["data"]
    included = data["included"]

    # Create a dictionary to map new_player_id to display_name and team
    player_data = {}
    for item in included:
        if item["type"] == "new_player":
            player_id = item["id"]
            display_name = item["attributes"]["display_name"]
            team = item["attributes"]["team"]
            player_data[player_id] = {"display_name": display_name, "team": team}
            
    # Create a dictionary to map stat_type id to name
    stat_type_data = {}
    for item in included:
        if item["type"] == "stat_type":
            stat_id = item["id"]
            stat_name = item["attributes"]["name"]
            stat_type_data[stat_id] = stat_name

    # Prepare data for the DataFrame
    pp_data = []
    for entry in entries:
        relationships = entry["relationships"]
        new_player_id = relationships["new_player"]["data"]["id"]
        
        # Retrieve display_name and team from the player_data dictionary
        display_name = player_data[new_player_id]["display_name"]
        team = player_data[new_player_id]["team"]
        
        # Retrieve stat_type name
        stat_type_id = relationships["stat_type"]["data"]["id"]
        stat_type_name = stat_type_data[stat_type_id]
        stat_type_name = pp_mapping.get(stat_type_name, stat_type_name)
        
        # Retrieve line_score
        line_score = entry["attributes"]["line_score"]

        pp_data.append({
            'Player_Name': display_name,
            'Team': team,
            'Prop': stat_type_name,
            'Line': line_score
        })

    return pp_data

data = fetch_pp_data()
df = pd.DataFrame(data)



'''
https://api.prizepicks.com/projections?league_id=7&per_page=250&state_code=TX&single_stat=true

'''
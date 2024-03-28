from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playergamelog
import pandas as pd
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.library.parameters import SeasonAll

#Create dictionaries that will hold a list of players and teams
player_dict = players.get_players()
team_dict = teams.get_teams()


# Filter active players
active_players = [player for player in player_dict if player['is_active']]

#Set display options for the command line, to display more lines.
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Print active players and their IDs
'''
for player in active_players:
    print(f"{player['full_name']} - ID: {player['id']}")
'''

#Returns a player_id based on their name
def find_player_id(name):
    player = [player for player in player_dict if player['full_name'] == name]
    return player[0]['id'] if player else None

#Returns player game logs based on their player_id and the season.
def get_player_game_logs(player_id, season):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    return game_logs.get_data_frames()[0]

#Returns a team_id based on the team name, can use either the full name or their abbreviation.
def find_team_id(team_name):
    team = [team for team in team_dict if team['full_name'] == team_name or team['abbreviation'] == team_name]
    return team[0]['id'] if team else None

#Returns the career stats for a player
def get_career_stats(player_id):
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    return career_stats.get_data_frames()[0]

#Returns a player's game logs against a specific team
def get_player_game_logs_against_team(player_id, team_abbreviation, season):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = game_logs.get_data_frames()[0]
    return df[df['MATCHUP'].str.contains(team_abbreviation)]

#Returns all of a player's previous games played against a team, as well as additional combo stats
def get_player_stats_against_team(player_id, team_abbreviation):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)
    df = game_logs.get_data_frames()[0]
    all_games = df[df['MATCHUP'].str.contains(team_abbreviation)]
    stats = all_games[['GAME_DATE','MATCHUP','MIN','PTS', 'REB', 'AST','FG3M','STL','BLK','TOV']].copy()
    stats.loc[:,'PTS + REB'] = stats['PTS'] + stats['REB']
    stats.loc[:,'PTS + AST'] = stats['PTS'] + stats['AST']
    stats.loc[:,'PTS + REB + AST'] = stats['PTS'] + stats['REB'] + stats['AST']
    stats.loc[:,'AST + REB'] = stats['AST'] + stats['REB']
    stats.loc[:,'BLK + STL'] = stats['BLK'] + stats['STL']
    return stats

#Returns a players averages against a team for a season
def get_player_averages_against_team(player_id, team_abbreviation, season):
    games_against_team = get_player_game_logs_against_team(player_id, team_abbreviation, season)
    games_against_team_stats = games_against_team[['MIN','FG3M','FTM','REB','AST','STL','BLK','TOV','PTS']]
    return games_against_team_stats.mean()

#Returns a team's current roster
def get_current_team_roster(team_id):
    roster = commonteamroster.CommonTeamRoster(team_id=team_id)
    return roster.get_data_frames()[0] 

#Returns stats and combo stats for a player's last five games in a season
def get_last_five_games_stats(player_id, season):
    # Fetching the player's game logs for the specified season
    game_logs = playergamelog.PlayerGameLog(player_id_nullable=player_id, season_nullable=season)
    df = game_logs.get_data_frames()[0]
    
    # Sorting the games by date and selecting the last five games
    last_five_games = df.head(5)
    # Extracting points, rebounds, and assists
    stats = last_five_games[['GAME_DATE','MATCHUP','MIN','PTS', 'REB', 'AST','FG3M','STL','BLK','TOV']].copy()
    stats.loc[:,'PTS + REB'] = stats['PTS'] + stats['REB']
    stats.loc[:,'PTS + AST'] = stats['PTS'] + stats['AST']
    stats.loc[:,'PTS + REB + AST'] = stats['PTS'] + stats['REB'] + stats['AST']
    stats.loc[:,'AST + REB'] = stats['AST'] + stats['REB']
    stats.loc[:,'BLK + STL'] = stats['BLK'] + stats['STL']
    return stats

#Returns stats and combo stats for a player in the 2023 season.
def get_current_game_logs(player_id):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=2023)
    df = game_logs.get_data_frames()[0]

    this_season = df
    stats = this_season[['GAME_DATE','MATCHUP','MIN','PTS', 'REB', 'AST','FG3M','STL','BLK','TOV']].copy()
    stats.loc[:,'PTS + REB'] = stats['PTS'] + stats['REB']
    stats.loc[:,'PTS + AST'] = stats['PTS'] + stats['AST']
    stats.loc[:,'PTS + REB + AST'] = stats['PTS'] + stats['REB'] + stats['AST']
    stats.loc[:,'AST + REB'] = stats['AST'] + stats['REB']
    stats.loc[:,'BLK + STL'] = stats['BLK'] + stats['STL']
    return stats


   

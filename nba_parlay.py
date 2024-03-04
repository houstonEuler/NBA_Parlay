import pandas as pd
import sqlite3
from ud2 import fetch_ud_data
from pp2 import fetch_pp_data
import nbaapi
import time
import logging


#Do I want stats to update first, or should I first get the list of players and update only their stats?
#Not having all player stats would make defensive analysis data incomplete, so it should probably run first.

# Insert call for nbastatsupdater.py
#
#
#


#Create connections to databases combodata.db has currently and former props/lines/odds from the DraftKings API, and nba_stats has NBA player stats from the nba_stats API (stored through nbaapi.py)
props_conn = sqlite3.connect('combodata.db')
stats_conn = sqlite3.connect('nba_stats.db')

#Create cursors for databases
props_cursor = props_conn.cursor()
stats_cursor = stats_conn.cursor()

#Use ud.py and pp.py to grab the manually-stored data from their websites
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
cur_prop_data = pd.read_sql_query("SELECT * FROM current_data", props_conn)

#Converts the Odds column to a numeric value for analysis
all_prop_data['Odds'] = pd.to_numeric(all_prop_data['Odds'], errors='coerce')
cur_prop_data['Odds'] = pd.to_numeric(cur_prop_data['Odds'], errors='coerce')

props_conn.close()

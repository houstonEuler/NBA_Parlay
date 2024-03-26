#Performs analysis of nba_stats.db
import nbaapi
import sqlite3
import time
import pandas as pd
import numpy as np

#Analyze player performance for each prop
def get_over_performance_for_player(player_id, prop, line):
    # Connect to the database
    conn = sqlite3.connect('nba_stats_old.db')
    cursor = conn.cursor()
    
    # Query to get the values of the specified column for the given player_id
    query = f"SELECT {prop} FROM player_game_logs WHERE player_id = ? AND {prop} > ?"
    cursor.execute(query, (player_id, line))

    # Fetch all the values of the specified column that are over the line
    over_values = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()
    
    return over_values

def get_under_performance_for_player(player_id, prop, line):
    # Connect to the database
    conn = sqlite3.connect('nba_stats_old.db')
    cursor = conn.cursor()
    
    # Query to get the values of the specified column for the given player_id
    query = f"SELECT {prop} FROM player_game_logs WHERE player_id = ? AND {prop} < ?"
    cursor.execute(query, (player_id, line))

    # Fetch all the values of the specified column that are over the line
    under_values = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()
    
    return under_values

def get_equal_performance_for_player(player_id, prop, line):
    # Connect to the database
    conn = sqlite3.connect('nba_stats.db')
    cursor = conn.cursor()
    
    # Query to get the values of the specified column for the given player_id
    query = f"SELECT {prop} FROM player_game_logs WHERE player_id = ? AND {prop} = ?"
    cursor.execute(query, (player_id, line))

    # Fetch all the values of the specified column that are over the line
    equal_values = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn.close()
    
    return equal_values
    


#Mean and Variance
def get_mean_variance_for_player(player_id, prop):
    # Connect to the database
    conn = sqlite3.connect('nba_stats.db')
    cursor = conn.cursor()
    
    # Query to get the values of the specified column for the given player_id
    query = f"SELECT {prop} FROM player_game_logs WHERE player_id = ?"
    cursor.execute(query, (player_id,))
    
    # Fetch all the values of the specified column
    values = [row[0] for row in cursor.fetchall()]
    
    # Calculate the mean
    mean = np.mean(values)
    
    # Calculate the variance of the mean
    variance = np.var(values)
    
    # Close the database connection
    conn.close()
    
    return mean, variance

#Median and Variance

def get_median_variance_for_player(player_id, prop):
    # Connect to the database
    conn = sqlite3.connect('nba_stats.db')
    cursor = conn.cursor()
    
    # Query to get the sorted values of the specified column for the given player_id
    query = f"SELECT {prop} FROM player_game_logs WHERE player_id = ? ORDER BY {prop}"
    cursor.execute(query, (player_id,))
    
    # Fetch all the values of the specified column
    values = [row[0] for row in cursor.fetchall()]
    
    # Calculate the median
    median = np.median(values)
    
    # Calculate the variance of the median
    variance = np.var(values)
    
    # Close the database connection
    conn.close()
    
    return median, variance


#Analyze opponent performance for each prop
def analyze_player_performance_by_matchup(matchup,prop):
    # Connect to the database
    conn = sqlite3.connect('nba_stats.db')
    
    # Query to calculate average of chosen stat grouped by matchup
    query = f"""
    SELECT ({matchup}), AVG({prop}) AS avg_{prop}
    FROM player_game_logs
    GROUP BY ({matchup})
    """
    
    # Execute the query and fetch the results into a DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Close the connection
    conn.close()
    
    return df


#(Do you need player position and starting status?  Is this available from nba_stats?)





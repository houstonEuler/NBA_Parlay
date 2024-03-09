#Performs analysis of nba_stats.db
import nbaapi
import sqlite3
import time
import pandas as pd
import numpy as np

#Analyze player performance for each prop


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

#(Do you need player position and starting status?  Is this available from nba_stats?)





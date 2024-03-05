#Performs analysis of nba_stats.db
import nbaapi
import sqlite3
import time
import pandas as pd


#Create connection to database
conn = sqlite3.connect('nba_stats.db')
cursor = conn.cursor()



#Analyze player performance for each prop


#Average


#Median


#Variance




#Analyze opponent performance for each prop

#(Do you need player position and starting status?  Is this available from nba_stats?)





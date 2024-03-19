#This script queries the DraftKings API for current betting odds every 5 minutes, and stores it in a database. It updates one table "current_data", with the the most recent props.
#It stores historical props in the propositions_data table.
#It's useful, because apps like Sleeper, which are only on mobile, will mirror DraftKings odds, and list props that are not available on Underdog or Prizepicks.

# Import necessary packages
import requests
import pandas as pd
import time
import sqlite3
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='dkapi2.log',  # if you want to write logs to a file
                    filemode='a')  # 'a' stands for append mode

# Connect to Database
conn = sqlite3.connect("combodata.db")
cursor = conn.cursor()

# Setup Tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS propositions_data (
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    Prop TEXT,
    Event_ID TEXT,
    Player_Name TEXT,
    Outcome TEXT,
    Odds TEXT,
    Line TEXT,
    Start_Date TEXT
);

CREATE TABLE IF NOT EXISTS current_data (
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    Prop TEXT,
    Event_ID TEXT,
    Player_Name TEXT,
    Outcome TEXT,
    Odds TEXT,
    Line TEXT,
    Start_Date TEXT
);

CREATE TABLE IF NOT EXISTS event_data (
    Event_ID TEXT,
    Start_Date TEXT,
    Game TEXT,
    Away_Team TEXT,
    Home_Team TEXT,
    Away_Team_Abbr TEXT,
    Home_Team_Abbr TEXT,
    Away_Team_ID TEXT,
    Home_Team_ID TEXT
);
""")

def fetch_data_from_api(api_url):
    try:
        response = requests.get(api_url)

        response.raise_for_status()

        return response.json()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    return None

propositions = [
                {'prop':'Points','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1215/subcategories/12488?format=json"},
                {'prop':'3-PT Made','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1218/subcategories/12497?format=json"},
                {'prop':'Pts + Reb + Asts','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/583/subcategories/5001?format=json"},
                {'prop':'Pts + Rebs','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/583/subcategories/9976?format=json"},
                {'prop':'Pts + Asts','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/583/subcategories/9973?format=json"},
                {'prop':'Ast + Rebs','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/583/subcategories/9974?format=json"},
                {'prop':'Rebounds','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1216/subcategories/12492?format=json"},
                {'prop':'Assists','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1217/subcategories/12495?format=json"},
                {'prop':'Steals','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1293/subcategories/13508?format=json"},
                {'prop':'Blocks','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1293/subcategories/13780?format=json"},
                {'prop':'Blocks + Steals','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1293/subcategories/13781?format=json"},
                {'prop':'Turnovers','url':"https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1293/subcategories/13782?format=json"},
]

dkapi_mapping = {
    'Threes':'3-PT Made',
    'Pts + Reb + Ast':'Pts + Reb + Asts',
    'Pts + Reb':'Pts + Rebs',
    'Pts + Ast':'Pts + Asts',
    'Ast + Reb':'Ast + Rebs',
    'Steals + Blocks':'Blocks + Steals'
    }

def fetch_dkapi_data():
    #List to store all data across props
    all_extracted_data = []
    logging.info("Starting to fetch data from API.")

    for proposition in propositions:
        data = fetch_data_from_api(proposition['url'])
        logging.info(f"Processing proposition: {proposition['prop']}")
        print(proposition['prop'])
        if not data:
            continue

        events = data['eventGroup'].get('events', [])

        update_event_data(events)

        not_started_events = {event['eventId']: event.get('startDate') for event in events if event.get('eventStatus', {}).get('state') == 'NOT_STARTED'}

        data2 = data['eventGroup']['offerCategories']

        # Filter categories for those with offerSubcategoryDescriptors
        categories_with_subcategories = [cat for cat in data2 if "offerSubcategoryDescriptors" in cat]

        # List to store extracted data
        extracted_data = []

        # Iterate over the categories with subcategories
        for category in categories_with_subcategories:
            for subcategory in category['offerSubcategoryDescriptors']:
                subcategory_name = subcategory['name']
                standardized_prop_name = dkapi_mapping.get(subcategory_name, subcategory_name)
                for offer in subcategory.get('offerSubcategory', {}).get('offers', []):
                    for bet in offer:
                        event_id = bet['eventId']

                        if event_id not in not_started_events:
                            continue

                        start_date = not_started_events[event_id]

                        for outcome in bet.get('outcomes', []):
                            participant_name = outcome['participants'][0]['name']
                            label = outcome['label']
                            odds_american = outcome['oddsAmerican']
                            line = outcome['line']
                            extracted_data.append({
                                'Prop': standardized_prop_name,
                                'Event_ID': event_id,
                                'Player_Name': participant_name,
                                'Outcome': label,
                                'Odds': odds_american,
                                'Line': line,
                                'Start_Date': start_date
                            })

        # Append extracted data of current proposition to the overall data list
        all_extracted_data.extend(extracted_data)
        
        logging.info("Sleeping for 30 seconds before next API call.")
        time.sleep(30)

    return all_extracted_data

def update_event_data(events):
    event_records = []
    for event in events:
        # Extracting event details
        event_record = {
            'Event_ID': event.get('eventId'),
            'Start_Date': event.get('startDate'),
            'Game': event.get('name'),
            'Away_Team': event.get('teamName1'),
            'Home_Team': event.get('teamName2'),
            'Away_Team_Abbr': event.get('teamShortName1'),
            'Home_Team_Abbr': event.get('teamShortName2'),
        'Away_Team_ID': event.get('team1', {}).get('teamId'),
        'Home_Team_ID': event.get('team2', {}).get('teamId')
        }
        event_records.append(event_record)
    
    if event_records:
        # Convert to DataFrame and update database
        event_df = pd.DataFrame(event_records)
        event_df.to_sql("event_data", conn, if_exists="replace", index=False)

def save_data_to_database(data):
    if data:
        # Convert the data to a DataFrame and write it to the propositions_data table
        df = pd.DataFrame(data)
        df.to_sql("propositions_data", conn, if_exists="append", index=False)
        
        # Refresh the current_data table
        cursor.execute("DELETE FROM current_data")
        df.to_sql("current_data", conn, if_exists="append", index=False)

if __name__ == '__main__':
    try:
        while True:
            data = fetch_dkapi_data()
            save_data_to_database(data)
            logging.info("Sleeping for 300 seconds before the next cycle.")
            time.sleep(300)
    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
    finally:
        # Close the database connection
        conn.close()


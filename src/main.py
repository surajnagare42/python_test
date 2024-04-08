import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import requests
from datetime import datetime, timedelta
import aiohttp
import asyncio
import os
import csv

def generate_dates(start_date_str, end_date_str):
    # Convert start and end date strings to datetime objects using the desired format
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    # Initialize list to store generated dates
    all_dates = []

    # Generate dates between start and end dates
    current_date = start_date
    while current_date < end_date:
        all_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return all_dates


# Function to check database connection
def check_database_connection(database_url):
    try:
        engine = create_engine(database_url)
        with engine.connect():
            return True
    except OperationalError:
        return False

async def fetch_data(session, date, api_key):
    url = f"http://api.exchangeratesapi.io/v1/{date}?access_key={api_key}&symbols=USD,GBP,EUR&format=1"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            return None

async def make_api_calls(dates):
    api_key = os.environ.get("API_KEY")
    if api_key is None:
        print("API_KEY environment variable is not set.")
        return None
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, date, api_key) for date in dates]
        results = await asyncio.gather(*tasks)
        return results

def write_to_csv(data, filename="exchange_rates.csv"):
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the full path for the CSV file
    filepath = os.path.join(output_dir, filename)

    # Define the CSV file header
    header = ["date", "base", "USD", "GBP", "EUR"]

    # Open the file in write mode
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header
        writer.writerow(header)
        
        # Iterate through each item in the data list
        for item in data:
            if item and 'success' in item and item['success']:
                # Extract the relevant data
                date = item['date']
                base = item['base']
                usd_rate = item['rates']['USD']
                gbp_rate = item['rates']['GBP']
                eur_rate = item['rates']['EUR']
                
                # Write the data row
                writer.writerow([date, base, usd_rate, gbp_rate, eur_rate])


def main():
    # Get database URL from environment variable
    database_url = os.environ.get("DATABASE_URL")
    if database_url is None:
        print("DATABASE_URL environment variable is not set.")
        return

    # Check database connection
    if check_database_connection(database_url):
        print("Database connection successful.")
    else:
        print("Failed to connect to the database.")
        return
    
    # Start date and end date
    start_date = os.environ.get("START_DATE")
    end_date = os.environ.get("END_DATE")

    # Make an API call
    dates = generate_dates(start_date, end_date)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(make_api_calls(dates))

    if results:
        print("API response:", results)
    else:
        print("Failed to fetch API data")

    # Write API response to a CSV file
    write_to_csv(results)
    

if __name__ == "__main__":
    main()

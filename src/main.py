import os
from sqlite3 import ProgrammingError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import requests
from datetime import datetime, timedelta
import aiohttp
import asyncio
import os
import csv
import psycopg2

def generate_dates(start_date_str, end_date_str):
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
        elif response.status == 429:  # Rate limit exceeded
            retry_after = int(response.headers.get('Retry-After', 10))  # Default to retry after 10 seconds
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            await asyncio.sleep(retry_after)
            return await fetch_data(session, date, api_key)
        elif response.status == 404:
            print("API data not found for:", date)
            return None
        elif response.status == 104:
            print("The maximum allowed API amount of monthly API requests has been reached.")
        elif response.status == 101:
            print("No API Key was specified or an invalid API Key was specified.")
        elif response.status == 103:
            print("The requested API endpoint does not exist.")
        elif response.status == 502:
            print("No or an invalid 'start_date' has been specified.")
        elif response.status == 502:
            print("No or an invalid 'end_date' has been specified.")
        else:
            print("API request failed with status code:", response.status)
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
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    header = ["date", "base", "USD", "GBP", "EUR"]

    # Open the file in write mode
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header
        writer.writerow(header)
        
        # Iterate through each item in the data list
        for item in data:
            if item and 'success' in item and item['success']:
                # Extract the exchange data
                date = item['date']
                base = item['base']
                usd_rate = item['rates']['USD']
                gbp_rate = item['rates']['GBP']
                eur_rate = item['rates']['EUR']
                writer.writerow([date, base, usd_rate, gbp_rate, eur_rate])

def create_exchange_rates_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    base VARCHAR(3) NOT NULL,
                    USD NUMERIC(10, 6) NOT NULL,
                    GBP NUMERIC(10, 6) NOT NULL,
                    EUR NUMERIC(10, 6) NOT NULL
                )
            """)
        conn.commit()
        print("Exchange rates table created successfully.")
    except Exception as e:
        print("Error creating exchange_rates table:", e)

def push_to_database(database_url):
    try:
        conn = psycopg2.connect(database_url)
        create_exchange_rates_table(conn)

        # Load CSV data into PostgreSQL table
        with open('output/exchange_rates.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  
            with conn.cursor() as cur:
                for row in reader:
                    date, base, usd, gbp, eur = row
                    sql = "INSERT INTO exchange_rates (date, base, USD, GBP, EUR) VALUES (%s, %s, %s, %s, %s)"
                    cur.execute(sql, (date, base, usd, gbp, eur))
        conn.commit()
        print("CSV data successfully pushed to PostgreSQL database.")
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
    finally:
        conn.close()


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
    # Push CSV data to MySQL database
    push_to_database(database_url)


if __name__ == "__main__":
    main()

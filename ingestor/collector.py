import time
import requests
import psycopg2
import os
from datetime import datetime

# 1. Configuration
# We read these from the environment variables set in docker-compose.yml
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "flight_data")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")

# Bounding Box (Roughly Switzerland area for testing - lots of traffic!)
# Min Lat, Min Lon, Max Lat, Max Lon
URL = "https://opensky-network.org/api/states/all"
PARAMS = {'lamin': 45.8, 'lomin': 5.9, 'lamax': 47.8, 'lomax': 10.5}


def get_db_connection():
    """Connect to the PostgreSQL database with retries."""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            print("✅ Connected to Database")
            return conn
        except psycopg2.OperationalError:
            print("⏳ Database not ready yet... waiting 5s")
            time.sleep(5)


def init_db(conn):
    """Create the table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS flight_logs (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        icao24 VARCHAR(50),
        callsign VARCHAR(50),
        lat FLOAT,
        lon FLOAT,
        altitude FLOAT,
        velocity FLOAT
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_table_query)
        conn.commit()
    print("✅ Table 'flight_logs' ensures.")


def fetch_and_store():
    conn = get_db_connection()
    init_db(conn)

    while True:
        try:
            print(f"📡 Fetching data from OpenSky at {datetime.now()}...")
            # Note: We use anonymous access (no auth). It has lower limits but is fine for testing.
            response = requests.get(URL, params=PARAMS, timeout=10)
            data = response.json()

            if 'states' in data and data['states']:
                flight_count = 0
                current_time = datetime.now()

                with conn.cursor() as cur:
                    for state in data['states']:
                        # state vector structure: [icao24, callsign, origin_country, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, ...]
                        icao24 = state[0]
                        callsign = state[1].strip() if state[1] else "Unknown"
                        lon = state[5]
                        lat = state[6]
                        alt = state[7]
                        vel = state[9]

                        # Only save if we have valid coordinates
                        if lat and lon:
                            cur.execute(
                                """
                                INSERT INTO flight_logs (timestamp, icao24, callsign, lat, lon, altitude, velocity)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """,
                                (current_time, icao24, callsign, lat, lon, alt, vel)
                            )
                            flight_count += 1

                    conn.commit()
                print(f"💾 Saved {flight_count} flights to DB.")
            else:
                print("⚠️ No flights found or API limit reached.")

        except Exception as e:
            print(f"❌ Error: {e}")
            # If DB connection died, try to reconnect
            if isinstance(e, psycopg2.OperationalError):
                conn = get_db_connection()

        # Wait 30 seconds before next fetch to respect API limits
        time.sleep(30)


if __name__ == "__main__":
    # Small delay to ensure DB container starts up first
    time.sleep(5)
    fetch_and_store()
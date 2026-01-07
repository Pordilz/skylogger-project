import streamlit as st
import pandas as pd
import psycopg2
import os
import time

# 1. Page Config
st.set_page_config(
    page_title="SkyLogger Pro",
    page_icon="✈️",
    layout="wide"
)

# 2. Database Connection
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "flight_data")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")


def get_data(limit=500):
    """Fetch flight records with error handling."""
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        query = f"SELECT * FROM flight_logs ORDER BY timestamp DESC LIMIT {limit}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()


# 3. Sidebar Controls
st.sidebar.header("🕹️ Control Panel")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 10)
min_altitude = st.sidebar.slider("Min Altitude (meters)", 0, 15000, 0)
show_raw = st.sidebar.checkbox("Show Raw Data", False)

# 4. Main Title
st.title("✈️ SkyLogger: Live Air Traffic Telemetry")
st.markdown(f"**Status:** Connected to Database | **Zone:** Central Europe")

# 5. Data Fetching & Filtering
df = get_data(1000)

if not df.empty:
    # Apply Filter (Logic Layer in Frontend)
    filtered_df = df[df['altitude'] >= min_altitude]

    # Top Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Logs", len(df))
    c2.metric("Visible Flights", filtered_df['icao24'].nunique())
    c3.metric("Avg Speed (m/s)", f"{filtered_df['velocity'].mean():.1f}")
    c4.metric("Highest Flight", f"{filtered_df['altitude'].max():.0f} m")

    # Main Layout
    col_map, col_details = st.columns([2, 1])

    with col_map:
        st.subheader(f"📍 Live Map (Flights > {min_altitude}m)")
        # Map only shows filtered flights
        st.map(filtered_df, latitude='lat', longitude='lon', size=40, color='#ff4b4b')

    with col_details:
        st.subheader("📋 Recent Traffic")
        display_cols = ['callsign', 'velocity', 'altitude', 'timestamp']
        st.dataframe(filtered_df[display_cols].head(15), hide_index=True)

    if show_raw:
        st.subheader("Raw Database Records")
        st.dataframe(df)

else:
    st.warning("Waiting for data... Ensure the 'Ingestor' container is running.")

# 6. Auto-Refresh Logic
time.sleep(refresh_rate)
st.rerun()
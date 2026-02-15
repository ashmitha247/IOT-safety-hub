import streamlit as st
import sqlite3
import pandas as pd
import time

# --- Page Configuration ---
st.set_page_config(page_title="IoT-Safety-Hub Dashboard", layout="wide")
st.title("🛡️ IoT-Safety-Hub: Industrial Safety Monitor")
st.markdown("Continuous monitoring and automated compliance logging for MSMEs.")

# --- Database Connection ---
# The dashboard looks back one folder to read the database created by the FastAPI backend
DB_PATH = "../backend/safety_hub_logs.db"

def fetch_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        # Fetch the latest 100 readings from the SQL Vault
        df = pd.read_sql_query("SELECT * FROM sensor_logs ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        return df
    except sqlite3.OperationalError:
        # Returns an empty dataframe if the database file hasn't been created yet
        return pd.DataFrame() 

# --- The "Refresh Cycle" (Continuous Polling) ---
# This creates a dynamic container that we will overwrite every 5 seconds
placeholder = st.empty()

with placeholder.container():
    df = fetch_data()

    if not df.empty:
        # 1. LIVE METRICS (Solving the "Reactive" Problem)
        st.subheader("Live Environment Status")
        latest = df.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        
        # Display current PPM. If MQ7 is over 50, show it in red/danger mode.
        col1.metric("CO Level (MQ-7)", f"{latest['mq7_ppm']} PPM", 
                    delta="DANGER" if latest['mq7_ppm'] >= 50 else "Safe", 
                    delta_color="inverse")
        col2.metric("Methane (MQ-4)", f"{latest['mq4_ppm']} PPM",
                    delta="Warning" if latest['mq4_ppm'] >= 25 else "Safe",
                    delta_color="inverse")
        col3.metric("Temperature", f"{latest['temperature']} °C")
        col4.metric("Humidity", f"{latest['humidity']} %")

        st.divider()

        # 2. BEHAVIORAL ANALYSIS (Visualizing the "Near-Misses")
        st.subheader("📈 Gas Concentration Trends (Behavioral Analysis)")
        # Reverse the dataframe so the graph plots chronologically (left to right)
        df_plot = df.iloc[::-1] 
        chart_data = df_plot.set_index('timestamp')[['mq7_ppm', 'mq4_ppm']]
        
        # Plotting the data. Red for CO, Orange for Methane.
        st.line_chart(chart_data, color=["#FF0000", "#FFA500"])

        st.divider()

        # 3. COMPLIANCE & AUDIT (Closing the "Audit Gap")
        st.subheader("📑 IS 14489:1998 Compliance Log")
        st.dataframe(df, use_container_width=True)

        # One-Click Export Feature for Inspectors
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Daily Audit Report (CSV)",
            data=csv,
            file_name="MSME_Safety_Audit_Report.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data found in the SQL Vault. Waiting for hardware signals...")

# --- Continuous Polling Loop ---
# This forces the Streamlit app to wait 5 seconds, then rerun the entire script
time.sleep(5)
st.rerun()
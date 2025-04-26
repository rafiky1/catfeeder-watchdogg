import streamlit as st
import requests
import pandas as pd
from PIL import Image
import os
from datetime import datetime, timedelta
import sqlite3
import plotly.express as px

API_URL = "http://localhost:8000"
SNAPSHOT_FOLDER = "snapshots"
REFRESH_INTERVAL = 20

st.set_page_config(page_title="CatFeeder Watchdog Dashboard", layout="wide")

# Auto-refresh HTML header
st.markdown(f"<meta http-equiv='refresh' content='{REFRESH_INTERVAL}'>", unsafe_allow_html=True)
st.title("🐾 CatFeeder Watchdog Dashboard")

# 🔹 SUMMARY
st.header("📊 Summary for Today")
try:
    res = requests.get(f"{API_URL}/summary")
    if res.ok and res.headers.get("Content-Type") == "application/json":
        summary = res.json()
        col1, col2 = st.columns(2)
        col1.metric("Total Feeding Sessions", summary.get("total_sessions", 0))
        col2.metric("Avg Duration (s)", summary.get("avg_duration", 0.0))
    else:
        st.error(f"❌ Unexpected response from /summary (status {res.status_code})")
except Exception as e:
    st.error(f"❌ Could not fetch summary: {e}")

conn = sqlite3.connect("detections.db")
df = pd.read_sql("SELECT timestamp FROM detections", conn)
conn.close()

df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
latest = df['timestamp'].max()
minutes_since = (datetime.now() - latest).total_seconds() / 60

if minutes_since > 180:
    st.error(f"🚨 The cat hasn't eaten in {int(minutes_since)} minutes!")
else:
    st.success(f"✅ Last feeding was {int(minutes_since)} minutes ago.")

# Fetch all session timestamps from FastAPI (create new endpoint or query DB directly)
try:
    sessions = requests.get(f"{API_URL}/trend").json().get("trend", {})
    if sessions:
        last_time_str = max(sessions.keys())
        last_time = datetime.strptime(last_time_str, "%H:%M")
        now = datetime.now().replace(second=0, microsecond=0)
        if now.hour != last_time.hour or now.minute != last_time.minute:
            last_full = datetime.combine(datetime.today(), last_time.time())
            hours_since = (now - last_full).total_seconds() / 3600
            if hours_since > 3:  # ⏱️ set your threshold here
                st.error(f"⚠️ No feeding detected in the last {int(hours_since)} hours!")
except:
    pass  # Fail silently if trend is empty or broken

# 🔹 TREND
st.subheader("📉 Feeding Activity Trend")

try:
    res = requests.get("http://localhost:8000/trend")
    if res.status_code == 200:
        data = res.json()
        if data:
            df = pd.DataFrame(data.items(), columns=["Time", "Sessions"])
            fig = px.line(df, x="Time", y="Sessions", markers=True)
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Feeding Sessions",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data yet.")
    else:
        st.error(f"❌ Unexpected response from /trend (status {res.status_code})")
except Exception as e:
    st.error(f"❌ Could not fetch trend data: {e}")


st.header("⏳ Meal Duration Categories")
try:
    durations = requests.get(f"{API_URL}/duration-categories").json()
    st.bar_chart(pd.DataFrame.from_dict(durations, orient="index", columns=["Sessions"]))
except:
    st.warning("Could not load duration categories.")

st.subheader("🕒 Feeding Time Distribution")

try:
    res = requests.get("http://localhost:8000/time-distribution")
    if res.status_code == 200:
        data = res.json()
        if data:
            df = pd.DataFrame(data.items(), columns=["Hour", "Sessions"])
            fig = px.bar(df, x="Hour", y="Sessions", text="Sessions")
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Feeding Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly feeding data yet.")
    else:
        st.error(f"❌ Unexpected response from /time-distribution (status {res.status_code})")
except Exception as e:
    st.error(f"❌ Could not fetch hourly data: {e}")


# 🔹 SNAPSHOTS
st.header("📸 Recent Snapshots")
if os.path.exists(SNAPSHOT_FOLDER):
    images = sorted(os.listdir(SNAPSHOT_FOLDER), reverse=True)[:5]
    img_cols = st.columns(len(images))
    for i, img_file in enumerate(images):
        img_path = os.path.join(SNAPSHOT_FOLDER, img_file)
        try:
            img = Image.open(img_path)
            img_cols[i].image(img, caption=img_file, use_container_width=True)
        except Exception as e:
            img_cols[i].error(f"Failed to load {img_file}: {e}")
else:
    st.warning("Snapshot folder not found.")

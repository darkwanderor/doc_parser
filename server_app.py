# streamlit_ui.py
import streamlit as st
import requests
import time

st.set_page_config(layout="wide")
st.title("📡 Live Request Viewer")
def format_log(log: dict) -> str:
    # Split and format the string manually
    try:
        parts = log.split(", ")
        return "\n".join(f"• {part}" for part in parts)
    except:
        return log  # fallback
# Server config
SERVER_URL = "http://localhost:8008/logs"

# Refresh control
refresh_interval = st.sidebar.slider("Refresh every (seconds)", 1, 10, 2)

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧾 CRM Requests")
    crm_display = st.empty()

with col2:
    st.subheader("🚨 Risk Alerts")
    risk_display = st.empty()
st.markdown("""
    <style>
    .stException {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# Auto-refreshing section
while True:
    try:
        res = requests.get(SERVER_URL)
        res.raise_for_status()
        logs = res.json()

        crm_logs = "\n\n".join(format_log(log) for log in logs.get("crm", []))
        risk_logs = "\n\n".join(format_log(log) for log in logs.get("risk_alert", []))

    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        crm_logs = "No CRM logs available."
        risk_logs = "No Risk Alert logs available."

    crm_display.text_area("Recent CRM Posts", value=crm_logs, height=400, key="crm_box")
    risk_display.text_area("Recent Risk Alerts", value=risk_logs, height=400, key="risk_box")

    time.sleep(refresh_interval)
    st.rerun()


    time.sleep(refresh_interval)
    st.rerun()

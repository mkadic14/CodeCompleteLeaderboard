import streamlit as st
import pandas as pd
import requests
import datetime
import time

# CONFIG
SUPABASE_URL = "https://terljxozssdrkzrwairb.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlcmxqeG96c3Nkcmt6cndhaXJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwOTI3OTYsImV4cCI6MjA2NTY2ODc5Nn0.U5DHcsKMsCC95UlHOJTKktznAz0b0ybpueXfQlxyFxQ"

# PAGE CONFIG
st.set_page_config(page_title="Leaderboard", layout="wide")
placeholder = st.empty()

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
}

# BACKGROUND IMAGE
bg_response = requests.get(
    f"{SUPABASE_URL}/rest/v1/background?select=pic&limit=1",
    headers=headers,
)
bg_url = None
if bg_response.status_code == 200 and len(bg_response.json()) > 0:
    bg_url = bg_response.json()[0]["pic"]

if bg_url:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: white;
        }}
        h1, h2, h3, h4, h5, h6, p, div, span {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Auto REFRESH
while True:
    with placeholder.container():
    st.markdown(
        f"""
        <div style='text-align:center;'>
            <h1 style='font-size: 3em;'>🏆 Code Complete Leaderboard 🏆</h1>
            <p style='font-size: 1.2em;'>Top 3 players – ranked by score and speed.</p>
            <p style='font-size: 1em;'>Auto-refreshed at {datetime.datetime.now().strftime('%H:%M:%S')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    url = f"{SUPABASE_URL}/rest/v1/rpc/get_leaderboard"
    response = requests.post(
        url,
        headers={**headers, "Content-Type": "application/json"},
        json={},
    )

    try:
        top_players = pd.DataFrame(response.json())

        if not top_players.empty:
            reordered = [
                top_players.iloc[1] if len(top_players) > 1 else None,
                top_players.iloc[0],
                top_players.iloc[2] if len(top_players) > 2 else None,
            ]

            cols = st.columns(3)
            for i, row in enumerate(reordered):
                with cols[i]:
                    if row is not None:
                        img_size = 150 if i != 1 else 200
                        rank = ["🥈", "🥇", "🥉"][i]

                        st.markdown(
                            f"""
                            <div style='text-align: center;'>
                                <h2>{rank} {row['playername']}</h2>
                                <img src="{row['picurl']}" width="{img_size}" style="border-radius: 10px; margin: 10px 0;" />
                                <p><b>Score:</b> {row['finalscore']}<br><b>Time:</b> {row['timetocomplete']}s</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("<div style='text-align: center;'>—</div>", unsafe_allow_html=True)
        else:
            st.warning("No players returned in leaderboard.")
    except Exception as e:
        st.error(f"Failed to parse leaderboard data.\n\nStatus: {response.status_code}\n\nError: {e}")

        # Wait nad rerun
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

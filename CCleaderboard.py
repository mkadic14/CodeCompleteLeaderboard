import streamlit as st
import pandas as pd
import requests
import datetime
import time

# CONFIG
SUPABASE_URL = "https://terljxozssdrkzrwairb.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlcmxqeG96c3Nkcmt6cndhaXJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwOTI3OTYsImV4cCI6MjA2NTY2ODc5Nn0.U5DHcsKMsCC95UlHOJTKktznAz0b0ybpueXfQlxyFxQ"
REFRESH_INTERVAL = 10  # seconds

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

# LOOP
while True:
    with placeholder.container():
        st.markdown(
            f"""
            <div style='text-align:center;'>
                <h1 style='font-size: 3em;'>:trophy: Code Complete Leaderboard :trophy:</h1>
                <p style='font-size: 1.2em;'>Top 3 players – ranked by score and speed.</p>
                <p style='font-size: 1em;'>Auto-refreshed at {datetime.datetime.now().strftime('%H:%M:%S')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ✅ JOINED QUERY TO FETCH TOP 3
        url = f"{SUPABASE_URL}/rest/v1/rpc/get_leaderboard"
        response = requests.post(
            url,
            headers={**headers, "Content-Type": "application/json"},
            json={},  # Empty payload if needed
        )

        if response.status_code == 200:
            top_players = pd.DataFrame(response.json())

            if len(top_players) == 3:
                reordered = [top_players.iloc[1], top_players.iloc[0], top_players.iloc[2]]
                cols = st.columns(3)

                for i, row in enumerate(reordered):
                    with cols[i]:
                        img_size = 150 if i != 1 else 200
                        rank = [":second_place_medal:", ":first_place_medal:", ":third_place_medal:"][i]

                        st.markdown(
                            f"""
                            <div style='text-align: center;'>
                                <h2>{rank} {row['playerName']}</h2>
                                <img src="{row['picURL']}" width="{img_size}" style="border-radius: 10px; margin: 10px 0;" />
                                <p><b>Score:</b> {row['finalScore']}<br><b>Time:</b> {row['timeToComplete']}s</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.warning("Not enough players to display a podium.")
        else:
            st.error(f"Leaderboard failed.\n\nStatus: {response.status_code}\n\n{response.text}")

    time.sleep(REFRESH_INTERVAL)
    st.rerun()
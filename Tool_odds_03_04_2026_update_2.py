import streamlit as st
import requests
import pandas as pd
import time
import streamlit.components.v1 as components

SPORT_ID = 1

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://1xfun888bet.com/",
    "Origin": "https://1xfun888bet.com"
}

st.set_page_config(page_title="TOOL_ODDS_FULL_BLACK_MR90", layout="wide")
st.title("⚽ TOOL ODDS FULL_BLACK MR90")
placeholder = st.empty()

# ================= GET MATCH LIST =================
def get_match_list():
    url = f"https://1xfun888bet.com/service-api/LiveFeed/Get1x2_VZip?sports={SPORT_ID}&count=30&lng=vi&gr=819&mode=4&country=43&virtualSports=true&noFilterBlockEvent=true"
    return requests.get(url, headers=headers).json().get("Value", [])

# ================= GET DETAIL =================
def get_match_detail(match_id):
    url = f"https://1xfun888bet.com/service-api/LiveFeed/GetGameZip?id={match_id}&lng=vi"
    return requests.get(url, headers=headers).json().get("Value", {})

# ================= FETCH =================
def fetch_football():
    rows = []

    matches = get_match_list()

    for m in matches:
        match_id = m.get("I")
        data = get_match_detail(match_id)

        if not data:
            continue

        league = data.get("LE", "")
        match_name = f"{data.get('O1')} vs {data.get('O2')}"

        sc = data.get("SC", {})
        minute = int(sc.get("TS", 0)) // 60

        score1 = sc.get("FS", {}).get("S1", 0)
        score2 = sc.get("FS", {}).get("S2", 0)
        score = f"{score1}-{score2}"

        markets = data.get("E", [])

        seen = set()

        for e in markets:
            g = e.get("G")
            t = e.get("T")
            line = e.get("P", 0)
            odd = e.get("C")

            if not (odd and 1.015 <= odd <= 1.02):
                continue

            if line is None or line <= 0:
                continue

            key = (match_name, line, odd)
            if key in seen:
                continue

            # ================= TEAM TOTAL (CHUẨN) =================
            if g == 62:
                team = "T1" if t in [13, 9] else "T2"

                rows.append({
                    "League": league,
                    "Match": match_name,
                    "Score": score,
                    "Bet": f"U{line} (TEAM {team})",
                    "Odds": odd,
                    "Half": "FT",
                    "Minute": minute
                })

                seen.add(key)
                continue

            # ================= TOTAL / TEAM T1 KHÔNG PHÂN BIỆT =================
            if g == 15 and t == 12:

                # 🔥 odds thấp => nghiêng về team 1 nhưng không chắc
                if 1.015 <= odd <= 1.02:
                    label = "TOTAL / TEAM T1"
                else:
                    label = "TOTAL"

                rows.append({
                    "League": league,
                    "Match": match_name,
                    "Score": score,
                    "Bet": f"U{line} ({label})",
                    "Odds": odd,
                    "Half": "FT",
                    "Minute": minute
                })

                seen.add(key)
                continue

        time.sleep(0.2)

    return rows

# ================= DATA =================
def get_data():
    return pd.DataFrame(fetch_football())

# ================= AUTO REFRESH =================
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="datarefresh")  # refresh mỗi 5 giây

# ================= LOOP (FIXED) =================
df = get_data()
current_time = time.strftime('%H:%M:%S')

placeholder.empty()

with placeholder.container():

    col1, col2 = st.columns(2)
    col1.metric("📊 Total Kèo", len(df))
    col2.metric("⏱ Time", current_time)

    if not df.empty:

        display_df = df[[
            "League",
            "Match",
            "Score",
            "Bet",
            "Odds",
            "Half",
            "Minute"
        ]]

        def highlight(row):
            if row["Odds"] == 1.016:
                return ["background-color: #00FF00; color: black;"] * len(row)

            if row["Odds"] == 1.015:
                return ["background-color: yellow; color: black; font-weight: bold;"] * len(row)

            return [""] * len(row)

        styled_df = display_df.style.apply(highlight, axis=1)

        st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning("⚠️ Không có kèo")
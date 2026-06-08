import pandas as pd
import streamlit as st
import base64
from Tabs.inpossession import render_in_possession
from Tabs.lineup import render_lineup
from Tabs.outofpossession import render_OOP
from Tabs.overview import  render_comprehensive_overview
from Module.data_loader import get_competitions, get_matches, get_raw_events, get_starting_xi
from config import DARK_CSS
from Tabs.transitions import render_transitions


# ── Streamlit App: PitchIQ ───────────────────────────────────────────────
st.set_page_config(
    page_title="PitchIQ",
    page_icon="⚽",
    layout="wide"
)
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.title("PitchIQ")
st.caption("Tactical Match Reports")
st.divider()

# sidebar: competition → season → match selection--------------------------
with st.sidebar:
    # ── Branding ──────────────────────────────────────────
    st.markdown("""
        <div style='text-align: center; padding: 8px 0 16px 0;'>
            <span style='font-size: 28px; font-weight: 800; color: #58a6ff;'>PitchIQ</span><br>
            <span style='font-size: 11px; color: #8b949e;'>Tactical Match Reports</span>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Step 1: Competition ───────────────────────────────
    st.markdown("#### 🔍 Select Match")
    df_competition = get_competitions()                          # cached
    comp_names = sorted(df_competition["competition_name"].unique())
    select_comp = st.selectbox("Competition", comp_names)

    # ── Step 2: Season ────────────────────────────────────
    filtered = df_competition[df_competition["competition_name"] == select_comp]
    season_names = sorted(filtered["season_name"].unique(), reverse=True)
    select_season = st.selectbox("Season", season_names)

    # ── Resolve IDs (single filter) ───────────────────────
    selection       = filtered[filtered["season_name"] == select_season].iloc[0]
    select_compid   = selection["competition_id"]
    select_seasonid = selection["season_id"]

    # ── Step 3: Team ──────────────────────────────────────
    df_matches = get_matches(select_compid, select_seasonid)     # cached
    df_matches = df_matches.sort_values("match_date", ascending=False)

    all_teams = sorted(pd.unique(
        df_matches[["home_team_name", "away_team_name"]].values.ravel("K")
    ))
    select_team = st.selectbox("Team", all_teams)

    # ── Step 4: Match ─────────────────────────────────────
    df_team_matches = df_matches[
        (df_matches["home_team_name"] == select_team) |
        (df_matches["away_team_name"] == select_team)
    ]

    match_options = (
        df_team_matches["match_date"].astype(str) + " · " +
        df_team_matches["home_team_name"] + " vs " +
        df_team_matches["away_team_name"]
    )
    select_match = st.selectbox("Match", match_options)

    # ── Resolve match ID safely ───────────────────────────
    match_label_to_id = dict(zip(match_options, df_team_matches["match_id"]))
    select_matchid    = match_label_to_id[select_match]
    match_row         = df_team_matches[df_team_matches["match_id"] == select_matchid].iloc[0]

    st.divider()
    st.caption(f"match id: {select_matchid}")
    home_team  = match_row["home_team_name"]
    away_team  = match_row["away_team_name"]    

# ── Clear stale cache on match change ─────────────────────
if st.session_state.get("current_match_id") != select_matchid:
    stale_keys = [
        k for k in st.session_state
        if k.startswith(("player_stats_", "attacking_", "defending_", "transitions_"))
    ]
    for k in stale_keys:
        del st.session_state[k]
    st.session_state["current_match_id"] = select_matchid


if "current_match_id" in st.session_state:
    st.markdown(f"""
        <div style='text-align: center; padding: 24px 0 8px 0;'>
            <div style='font-size: 36px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.5px;'>
                {match_row['home_team_name']}
                <span style='color: #3b82f6; margin: 0 16px;'>
                    {int(match_row['home_score'])} – {int(match_row['away_score'])}
                </span>
                {match_row['away_team_name']}
            </div>
            <div style='margin-top: 10px; font-size: 13px; color: #64748b; letter-spacing: 0.03em;'>
                📅 {match_row['match_date']} &nbsp;·&nbsp; 🏆 {select_comp} &nbsp;·&nbsp; 🗓️ {select_season}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()


df_events,df_related,df_freeze,df_tactics = get_raw_events(select_matchid)
passes = df_events[df_events['type_name']=='Pass']
shots = df_events[df_events['type_name']=='Shot']
carries = df_events[df_events['type_name']=='Carry']
pressures = df_events[df_events['type_name']=='Pressure']
dribbles = df_events[df_events['type_name']=='Dribble']
def_actions = df_events[(df_events['type_name']=='Interception') | (df_events['type_name']=='Clearance') | (df_events['type_name']=='Block') | (df_events['type_name']=='Ball Recovery') | (df_events['type_name']=='Duel')]
turnovers = df_events[(df_events['type_name']=='Dispossession') | (df_events['type_name']=='Misconduct')]

xi = get_starting_xi(select_matchid)


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Lineups & Structure", "In Possession","Out of Possession", "Transitions"]
)

with tab1:
    # ── Overview ─────────────────────────────────────────────
    st.title("Match Overview")
    render_comprehensive_overview(df_events, passes, shots, pressures, def_actions, home_team, away_team)

with tab2:
    # ── Lineups & Structure ─────────────────────────────────
    st.title("Lineup & Structures")
    render_lineup(df_events, xi, home_team, away_team,match_row)

with tab3:
    # ── In Possession ───────────────────────────────────────
    st.title("In Possession")
    render_in_possession(passes, shots, carries, home_team, away_team)

with tab4:
    # ── Out of Possession ─────────────────────────────────
    st.title("Out of Possession")
    render_OOP(df_events, pressures, def_actions, passes, home_team, away_team)

with tab5:
    # ── Transitions ───────────────────────────────────────
    st.title("Transitions")
    render_transitions(df_events, home_team, away_team, select_matchid)


with open("Data\open-data-master\img\SB - Icon Lockup - Colour positive.png", "rb") as f:
    data = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="text-align:center; font-size:0.85rem; color:#9CA3AF;">
        Powered by StatsBomb Open Data<br>
        <img src="data:image/png;base64,{data}" width="120"><br><br>
        Tactical Match Reports<br>
        Built by <b>Bryant Andersson Tantra</b><br>
        <a href="https://github.com/anderssonbryant" target="_blank">GitHub</a> |
        <a href="https://www.linkedin.com/in/bryant-andersson-tantra-73a5291b2/" target="_blank">LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True
)

# tabs/attacking.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from Module.chart import (
    plot_final_third_entries,
    plot_shot_map,
    plot_box_entries,
    plot_carry_map,
)
from config import HOME_COLOR, AWAY_COLOR


def render_in_possession(passes, shots, carries, home_team, away_team):

    # ── Team toggle ───────────────────────────────────────
    team = st.radio(
        "Team",
        [home_team, away_team],
        horizontal=True,
        label_visibility="collapsed",
        key="attacking_team_toggle"
    )
    color = HOME_COLOR if team == home_team else AWAY_COLOR

    # ── Fetch data ────────────────────────────────────────
    passes  = passes[passes['team_name'] == team]
    shots   = shots[shots['team_name'] == team]
    carries = carries[carries['team_name'] == team]

    # ── Computed metrics ──────────────────────────────────
    completed   = passes[passes['outcome_name'].isna()]
    pass_pct    = round(len(completed) / len(passes) * 100, 1) \
                  if len(passes) else 0
    prog_passes = passes[
        (passes['end_x'] - passes['x'] > 10) &
        (passes['end_x'] >= 80)
    ] if 'end_x' in passes.columns else pd.DataFrame()
    key_passes  = passes[passes['pass_goal_assist'].notna()] 
    xG          = round(float(
        shots['shot_statsbomb_xg'].sum()
    ), 2) if 'shot_statsbomb_xg' in shots.columns else 0

    # ── Metric row ────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Passes",       len(passes))
    c2.metric("Pass Cmp %",   f"{pass_pct}%")
    c3.metric("Prog. Passes", len(prog_passes))
    c4.metric("Key Passes",   len(key_passes))
    c5.metric("Shots",        len(shots))
    c6.metric("xG",           f"{xG:.2f}")

    st.divider()

    # ── Row 1: Final Third Entries + Shot Map ─────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Final Third Entries")
        st.caption("🔵 Passes &nbsp; 🟡 Carries")
        fig = plot_final_third_entries(passes, carries, color)
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.markdown("#### Shot Map")
        fig = plot_shot_map(shots, team, color)
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # ── Row 2: Box Entries + Progressive Carries ──────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Progressive Carries")
        st.caption("🔵 Progressive &nbsp; 🟡 Into box")
        fig = plot_carry_map(carries, team, color)
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.markdown("#### Box Entries")
        st.caption("🔵 Passes &nbsp; 🟡 Carries")
        fig = plot_box_entries(passes, carries, color)
        st.pyplot(fig)
        plt.close(fig)

    
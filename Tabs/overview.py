# utils/stats_comparison.py
import pandas as pd
from Module.chart import plot_momentum, plot_shot_timeline, plot_xg_story
from Module.data_loader import get_events_only, get_shots
from Module.metrics import compute_match_stats
import streamlit as st
from config import HOME_COLOR, AWAY_COLOR, TEXT_PRIMARY, TEXT_SECONDARY


def render_stat_comparison(home_stats, away_stats, home_team, away_team):
    stat_labels = [
        ('shots',         'Shots'),
        ('sot',           'Shots on Target'),
        ('xG',            'Expected Goals (xG)'),
        ('goals',         'Goals'),
        ('big_chances',   'Big Chances'),
        ('passes',        'Passes'),
        ('pass_pct',      'Pass Completion %'),
        ('prog_passes',   'Progressive Passes'),
        ('key_passes',    'Key Passes'),
        ('pressures',     'Pressures'),
        ('tackles',       'Tackles'),
        ('interceptions', 'Interceptions'),
        ('clearances',    'Clearances'),
        ('blocks',        'Blocks'),
    ]

    # ── Header ────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 3, 2])
    col1.markdown(
        f"<div style='color:#3b82f6; font-weight:700; font-size:15px;'>{home_team}</div>",
        unsafe_allow_html=True
    )
    col2.markdown(
        "<div style='text-align:center; color:#64748b; font-size:13px;"
        "text-transform:uppercase; letter-spacing:0.08em;'>MATCH STATISTICS</div>",
        unsafe_allow_html=True
    )
    col3.markdown(
        f"<div style='text-align:right; color:#f97316; font-weight:700; font-size:15px;'>{away_team}</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ── Stat rows ─────────────────────────────────────────
    for stat_key, stat_name in stat_labels:
        home_val = home_stats.get(stat_key, 0)
        away_val = away_stats.get(stat_key, 0)
        total    = home_val + away_val if (home_val + away_val) > 0 else 1
        home_pct = float(home_val) / float(total)

        # Format display value
        if isinstance(home_val, float):
            home_display = f"{home_val:.2f}"
            away_display = f"{away_val:.2f}"
        else:
            home_display = str(home_val)
            away_display = str(away_val)

        col1, col2, col3 = st.columns([2, 3, 2])

        # Home value — right aligned, blue
        col1.markdown(
            f"<div style='font-size:20px; font-weight:700; color:#3b82f6;"
            f"text-align:right; padding-right:8px;'>{home_display}</div>",
            unsafe_allow_html=True
        )

        # Stat name + progress bar
        with col2:
            st.markdown(
                f"<div style='text-align:center; font-size:11px; color:#64748b;"
                f"margin-bottom:4px; letter-spacing:0.03em;'>{stat_name}</div>",
                unsafe_allow_html=True
            )
            st.progress(home_pct)

        # Away value — left aligned, orange
        col3.markdown(
            f"<div style='font-size:20px; font-weight:700; color:#f97316;"
            f"text-align:left; padding-left:8px;'>{away_display}</div>",
            unsafe_allow_html=True
        )

def render_comprehensive_overview(events,passes, shots, pressures, def_actions, home_team, away_team):

    #-Plot Monmentum -------------------------------
    st.markdown("#### Match Momentum")
    fig = plot_momentum(events, home_team, away_team)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("#### xG Match Story")
    fig = plot_xg_story(shots, home_team, away_team)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    home_stats = compute_match_stats(passes, shots, pressures, def_actions,home_team)
    away_stats = compute_match_stats(passes, shots, pressures, def_actions,away_team)

                # ── Render comparison ─────────────────────────────────
    render_stat_comparison(home_stats, away_stats, home_team, away_team)
    st.divider()


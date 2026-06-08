# tabs/defending.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from Module.chart import (
    plot_pressure_heatmap,
    plot_high_press_map,
    plot_defensive_actions_map,
    plot_recovery_map,
    plot_shots_allowed,
    plot_tackle_interception_map,
)
from Module.metrics import compute_ppda
from config import HOME_COLOR, AWAY_COLOR


def render_OOP(events,pressures,def_acts,passes,home_team, away_team):

    # ── Team toggle ───────────────────────────────────────
    team = st.radio(
        "Team",
        [home_team, away_team],
        horizontal=True,
        key="defending_team_toggle",
        label_visibility="collapsed"
    )
    color = HOME_COLOR if team == home_team else AWAY_COLOR

    # ── Computed metrics ──────────────────────────────────
    def_acts_team = def_acts[def_acts["team_name"] == team]
    pressures_team = pressures[pressures["team_name"] == team]
    tackles_team       = def_acts_team[(def_acts_team['sub_type_name'] == 'Tackle') ]
    interceptions_team = def_acts_team[(def_acts_team['type_name'] == 'Interception') ]
    clearances_team    = def_acts_team[(def_acts_team['type_name'] == 'Clearance') ]
    blocks_team        = def_acts_team[(def_acts_team['type_name'] == 'Block') ]
    ppda          = compute_ppda(passes, pressures, def_acts, team)


    # ── Metric row ────────────────────────────────────────
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Pressures",     len(pressures_team))
    c2.metric("PPDA",          f"{ppda:.1f}" if ppda else "N/A",
              help="Lower = more intense press")
    c3.metric("Tackles",       len(tackles_team))
    c4.metric("Interceptions", len(interceptions_team))
    c5.metric("Clearances",    len(clearances_team))
    c6.metric("Blocks",        len(blocks_team))

    # ── PPDA context ──────────────────────────────────────
    if ppda:
        if ppda < 7:
            ppda_label = "🔥 Elite press"
            ppda_color = "#3fb950"
        elif ppda < 9:
            ppda_label = "✅ Good press"
            ppda_color = "#58a6ff"
        elif ppda < 12:
            ppda_label = "⚠️ Moderate press"
            ppda_color = "#f59e0b"
        else:
            ppda_label = "❌ Low press intensity"
            ppda_color = "#f97316"

        st.markdown(
            f"<div style='font-size:12px; color:{ppda_color};"
            f"margin-bottom:8px;'>"
            f"Press Rating: <b>{ppda_label}</b> "
            f"(PPDA {ppda:.1f} — lower is better)</div>",
            unsafe_allow_html=True
        )

    st.divider()

    # ─────────────────────────────────────────────────────
    # ROW 1 — Pressure Heatmap + High Press Map
    # Pressure heatmap = full picture of where team pressed
    # High press map = only opponent half pressures
    # Together they show both volume and location of press
    # ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Pressure Heatmap")
        st.caption(
            "Where the team applied pressure across the full pitch. "
            "Red zones = highest pressure concentration."
        )
        fig = plot_pressure_heatmap(pressures_team, team, color)
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.markdown("#### High Press Map")
        st.caption(
            "Pressures in the opponent's half only. "
            "Shows how aggressively the team pressed high."
        )
        fig = plot_high_press_map(pressures_team, team, color)
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # ─────────────────────────────────────────────────────
    # ROW 2 — Defensive Actions + Recovery Map
    # Actions map = all types of defensive involvement
    # Recovery map = specifically where ball was won back
    # ─────────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Defensive Actions Map")
        st.caption(
            "🔵 Tackle &nbsp; 🟢 Interception &nbsp; "
            "🟡 Clearance &nbsp; ⬜ Block &nbsp; 🟣 Recovery"
        )
        fig = plot_defensive_actions_map(def_acts_team, team, color)
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.markdown("#### Ball Recovery Map")
        st.caption(
            "Where the team won the ball back. "
            "🟢 Opponent half &nbsp; "
            "🔵 Midfield &nbsp; "
            "🟠 Own half."
        )
        fig = plot_recovery_map(def_acts_team, color)
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # ─────────────────────────────────────────────────────
    # ROW 3 — Shots Allowed + Tackle & Interception Map
    # Shots allowed = defensive vulnerability view
    # Tackle/intercept = where ball was actively won
    # ─────────────────────────────────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("#### Shots Allowed")
        st.caption(
            "Shots the opponent took against this team. "
            "⭐ Goal conceded &nbsp; "
            "🔵 Saved &nbsp; "
            "🔴 Off target."
        )
        fig = plot_shots_allowed(events, team, color)
        st.pyplot(fig)
        plt.close(fig)

    with col6:
        st.markdown("#### Tackles & Interceptions")
        st.caption(
            "Ball-winning actions only. "
            "🔵 Tackle &nbsp; 🟢 Interception. "
            "Green shading = zones of highest activity."
        )
        fig = plot_tackle_interception_map(tackles_team, interceptions_team, color)
        st.pyplot(fig)
        plt.close(fig)
# tabs/transitions.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from Module.data_loader import get_events_only
from Module.metrics import build_transition_metrics
from Module.chart import (
    plot_counter_attack_map,
    plot_opp_counter_map,
    plot_counter_timeline,
    plot_counter_zone_breakdown,
)
from config import HOME_COLOR, AWAY_COLOR


def render_transitions(events, home, away, match_id):

    # ── Team toggle ───────────────────────────────────────
    team = st.radio(
        "Team",
        [home, away],
        horizontal=True,
        key="transitions_toggle",
        label_visibility="collapsed"
    )
    color = HOME_COLOR if team == home else AWAY_COLOR

    # ── Cache per team per match ──────────────────────────
    cache_key = f"transitions_{match_id}_{team}"
    if cache_key not in st.session_state:
        with st.spinner("Computing transition metrics..."):
            st.session_state[cache_key] = \
                build_transition_metrics(events, team)

    m = st.session_state[cache_key]

    # ─────────────────────────────────────────────────────
    # SECTION 1 — Counter Timeline
    # Full match view of when counters happened.
    # Own counters above zero, opponent below.
    # Dot size = xG of that counter possession.
    # Shows which team was more dangerous in transitions
    # and WHEN in the match transitions were most frequent.
    # ─────────────────────────────────────────────────────
    st.markdown("### ⚡ Transition Timeline")
    st.caption(
        "Each dot = one counter-attack possession. "
        "Above line = this team's counters. "
        "Below line = opponent's counters. "
        "Dot size = xG. ⭐ = goal."
    )

    fig = plot_counter_timeline(
        m['df_counters'], m['df_opp_counters'],
        home, away, team, color
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ─────────────────────────────────────────────────────
    # SECTION 2 — Attacking Transitions
    # All counter possessions labeled 'From Counter'
    # by StatsBomb — their own ground truth classification.
    # Efficiency = % of counters that reached a shot.
    # Conversion = % of counters that led to a goal.
    # ─────────────────────────────────────────────────────
    st.markdown("### 🏃 Attacking Transitions")
    st.caption(
        "Based on StatsBomb's own 'From Counter' possession "
        "classification — more accurate than manual detection."
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Counters",       m['counters_initiated'])
    c2.metric("Led to Shot",    m['counters_to_shot'])
    c3.metric("Led to Goal",    m['counters_to_goal'])
    c4.metric("Efficiency",     f"{m['counter_efficiency']}%",
              help="% of counters that reached a shot")
    c5.metric("Counter xG",     f"{m['counter_xg']:.2f}")
    c6.metric("Avg Duration",   f"{m['avg_duration']}s",
              help="Average seconds per counter possession")

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### Counter-Attack Map")
        st.caption(
            "Arrow = direction + distance of each counter. "
            "⭐ Gold star = goal. "
            "Gold arrow = shot. "
            "Faded = no shot."
        )
        fig = plot_counter_attack_map(
            m['df_counters'], color
        )
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.markdown("#### By Starting Zone")
        st.caption(
            "High = won ball in opponent half. "
            "Mid = midfield. Low = own half. "
            "Shows which zone generates most danger."
        )
        fig = plot_counter_zone_breakdown(m['df_counters'])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough counter data.")

    st.divider()

    # ── Counter possession detail table ───────────────────
    if not m['df_counters'].empty:
        with st.expander("📋 Counter-Attack Detail"):
            st.caption(
                "Every counter-attack possession. "
                "Sorted by minute."
            )
            display = m['df_counters'][[
                'minute', 'start_x', 'distance_gained',
                'n_passes', 'n_carries', 'n_shots',
                'xg', 'led_to_shot', 'led_to_goal',
                'duration_sec', 'zone',
            ]].copy()

            display.columns = [
                "Min", "Start X", "Distance",
                "Passes", "Carries", "Shots",
                "xG", "Shot?", "Goal?",
                "Duration(s)", "Zone",
            ]
            display["Start X"]  = display["Start X"].round(1)
            display["Distance"] = display["Distance"].round(1)
            display["xG"]       = display["xG"].round(2)

            st.dataframe(
                display.sort_values("Min").set_index("Min"),
                use_container_width=True
            )

    st.divider()

    # ─────────────────────────────────────────────────────
    # SECTION 3 — Defending Transitions
    # Opponent's counter possessions against this team.
    # Shows how vulnerable the team is in transition.
    # opp_efficiency = % of opponent counters that
    # resulted in a shot against us.
    # ─────────────────────────────────────────────────────
    st.markdown("### 🛡️ Defending Transitions")
    st.caption(
        "Opponent counter-attacks against this team. "
        "Shows defensive transition vulnerability."
    )

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Opp Counters",    m['opp_counters'])
    d2.metric("Led to Shot",     m['opp_counters_to_shot'])
    d3.metric("Goals Conceded",  m['opp_counters_to_goal'])
    d4.metric("Opp Efficiency",  f"{m['opp_vulnerability']}%",
              help="% of opponent counters that reached a shot")
    d5.metric("xG Conceded",     f"{m['xg_conceded_counter']:.2f}")

    st.divider()

    # ── Vulnerability rating ───────────────────────────────
    eff = m['opp_vulnerability']
    if eff == 0:
        label      = "✅ No counter-attacks conceded"
        label_color = "#3fb950"
    elif eff < 20:
        label      = "✅ Well protected in transitions"
        label_color = "#3fb950"
    elif eff < 35:
        label      = "⚠️ Moderate transition vulnerability"
        label_color = "#f59e0b"
    else:
        label      = "❌ High transition vulnerability"
        label_color = "tomato"

    st.markdown(
        f"<div style='font-size:12px; color:{label_color}; "
        f"margin-bottom:12px;'>"
        f"{label} — {eff}% of opponent counters reached a shot"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Opponent counter map ───────────────────────────────
    st.markdown("#### Opponent Counter-Attack Starting Locations")
    st.caption(
        "Where opponent counter-attacks originated. "
        "🔴 Red = led to shot against us. "
        "⭐ Gold = goal conceded. "
        "Dim = no shot."
    )

    fig = plot_opp_counter_map(m['df_opp_counters'], color)
    st.pyplot(fig)
    plt.close(fig)

    # ── Opponent detail table ──────────────────────────────
    if not m['df_opp_counters'].empty:
        with st.expander("📋 Opponent Counter Detail"):
            display = m['df_opp_counters'][[
                'minute', 'start_x', 'n_shots',
                'xg_conceded', 'led_to_shot',
                'led_to_goal', 'duration_sec',
            ]].copy()
            display.columns = [
                "Min", "Start X", "Shots",
                "xG Conceded", "Shot?", "Goal?",
                "Duration(s)",
            ]
            display["Start X"]     = display["Start X"].round(1)
            display["xG Conceded"] = display["xG Conceded"].round(2)

            st.dataframe(
                display.sort_values("Min").set_index("Min"),
                use_container_width=True
            )

    st.divider()

    # ─────────────────────────────────────────────────────
    # SECTION 4 — Transition Balance
    # Head to head comparison of both teams' counter
    # effectiveness in a single view.
    # ─────────────────────────────────────────────────────
    st.markdown("### ⚖️ Transition Balance")
    st.caption(
        "Head-to-head comparison of both teams' "
        "counter-attack effectiveness."
    )

    opponent = away if team == home else home

    balance_data = {
        'Metric': [
            'Counter-Attacks',
            'Shots from Counter',
            'Goals from Counter',
            'Counter xG',
            'Avg Duration (s)',
        ],
        team: [
            m['counters_initiated'],
            m['counters_to_shot'],
            m['counters_to_goal'],
            f"{m['counter_xg']:.2f}",
            f"{m['avg_duration']}s",
        ],
        opponent: [
            m['opp_counters'],
            m['opp_counters_to_shot'],
            m['opp_counters_to_goal'],
            f"{m['xg_conceded_counter']:.2f}",
            f"{m['avg_opp_duration']}s",
        ]
    }

    balance_df = pd.DataFrame(balance_data)

    # Render as styled comparison
    for _, row in balance_df.iterrows():
        bc1, bc2, bc3 = st.columns([2, 1, 1])
        bc1.markdown(
            f"<div style='color:#64748b; font-size:12px; "
            f"padding-top:6px;'>{row['Metric']}</div>",
            unsafe_allow_html=True
        )
        bc2.markdown(
            f"<div style='color:{color}; font-weight:700; "
            f"font-size:16px; text-align:center;'>"
            f"{row[team]}</div>",
            unsafe_allow_html=True
        )
        bc3.markdown(
            f"<div style='color:tomato; font-weight:700; "
            f"font-size:16px; text-align:center;'>"
            f"{row[opponent]}</div>",
            unsafe_allow_html=True
        )


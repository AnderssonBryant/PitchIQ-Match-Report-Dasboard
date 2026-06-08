# tabs/lineup.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from Module.chart import (
    plot_lineup,
    plot_pass_network,
    plot_average_positions,
    plot_substitution_timeline,
    plot_formation_timeline,
)
from config import HOME_COLOR, AWAY_COLOR


def render_lineup(events,xi,home,away,match_row):

    home_data      = xi.get(home, {})
    away_data      = xi.get(away, {})
    home_formation = home_data.get('formation', '—')
    away_formation = away_data.get('formation', '—')
    home_lineup    = home_data.get('lineup', [])
    away_lineup    = away_data.get('lineup', [])

    # ─────────────────────────────────────────────────────
    # SECTION 1 — Starting Formations
    # Shows how each team lined up at kick-off.
    # Dot size is equal for all — this is the intended
    # plan. Actual positions are in Section 3 below.
    # ─────────────────────────────────────────────────────
    st.markdown("### 🟢 Starting Formations")
    st.caption(
        "Player positions based on the Starting XI event. "
        "Scroll down for actual average positions during the match."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {home}")
        st.caption(f"Formation: **{home_formation}**")
        if home_lineup:
            fig = plot_lineup(home_lineup, HOME_COLOR, flip=False)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Lineup data unavailable.")

    with col2:
        st.markdown(f"#### {away}")
        st.caption(f"Formation: **{away_formation}**")
        if away_lineup:
            fig = plot_lineup(away_lineup, AWAY_COLOR, flip=True)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Lineup data unavailable.")

    st.divider()

    # ─────────────────────────────────────────────────────
    # SECTION 2 — Formation Timeline
    # Shows if and when either team changed their shape.
    # A 4-3-3 that became 5-4-1 after conceding is a
    # key tactical story. Powered by Tactical Shift events.
    # Only appears when a tactical shift was recorded.
    # ─────────────────────────────────────────────────────
    st.markdown("### 🔄 Formation Timeline")
    st.caption(
        "Tracks formation changes throughout the match. "
        "Changes appear as dashed vertical lines with the minute. "
        "If no changes occurred, only the starting formation shows."
    )

    fig = plot_formation_timeline(events, match_row)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tactical shifts recorded for this match.")

    st.divider()

    # ─────────────────────────────────────────────────────
    # SECTION 3 — Pass Network + Average Positions
    # Pass network = who connected with who and how often.
    # Thicker lines = stronger connection between players.
    # Average positions = where players actually operated
    # on average during the match — often very different
    # from their listed position in Section 1.
    # Larger dots = more touches in that position.
    # ─────────────────────────────────────────────────────
    st.markdown("### 🔗 In-Game Structure")
    st.caption(
        "Pass network shows connections between players — "
        "thicker lines mean more passes between that pair. "
        "Average positions show where each player operated "
        "on average — larger dots mean more touches."
    )

    team_structure = st.radio(
        "Select Team",
        [home, away],
        horizontal=True,
        key="structure_toggle",
        label_visibility="collapsed"
    )
    color_structure = HOME_COLOR \
                      if team_structure == home else AWAY_COLOR

    passes_team = events[
        (events['type_name'] == 'Pass') &
        (events['team_name'] == team_structure)
    ].copy()

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Pass Network")
        st.caption(
            "Node size reflects number of passes made. "
            "Line thickness reflects pass volume between pairs. "
            "Only connections with more than 3 passes shown."
        )
        fig = plot_pass_network(
            passes_team, team_structure, color_structure
        )
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.markdown("#### Average Positions")
        st.caption(
            "Mean x,y position across all touch events. "
            "Compare with Section 1 to see how much "
            "players drifted from their listed positions."
        )
        fig = plot_average_positions(
            events, team_structure, color_structure
        )
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # ─────────────────────────────────────────────────────
    # SECTION 4 — Substitution Timeline
    # Shows exactly when subs happened for both teams.
    # ⬆️ Green triangle = player coming ON
    # ⬇️ Red triangle   = player going OFF
    # Coaches cross-reference this with the momentum
    # chart to judge whether subs changed the game.
    # ─────────────────────────────────────────────────────
    st.markdown("### 🔃 Substitution Timeline")
    st.caption(
        "⬆️ Green = player coming on &nbsp;·&nbsp; "
        "⬇️ Red = player going off. "
        "Hover over markers for player names and exact minute."
    )

    fig = plot_substitution_timeline(events, match_row)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No substitutions recorded in this match.")

    st.divider()


    # ─────────────────────────────────────────────────────
    # SECTION 5 — Squad Lists
    # Full squad list for both teams including subs.
    # Starters shown in full white — normal brightness.
    # Substitutes dimmed in grey — visually separated.
    # Position abbreviation from POSITION_COORDS dict.
    # Sorted: starters first by jersey number,
    #         then subs by jersey number.
    # ─────────────────────────────────────────────────────
  # ── Player tables ─────────────────────────────────────
    st.markdown("### 📋 Squad Lists")
    st.caption("Full matchday squad including substitutes.")

    tcol1, tcol2 = st.columns(2)

    for col, team, lineup in [
        (tcol1, home, home_lineup),
        (tcol2, away, away_lineup)
    ]:
        with col:
            st.markdown(f"**{team}**")
            if lineup:
                df = pd.DataFrame(lineup)

                # Display name — nickname or surname
                df['display_name'] = df.apply(
                    lambda r: r['player_nickname']
                    if r.get('player_nickname') and
                       str(r['player_nickname']).strip() not in
                       ['', 'nan', 'None']
                    else r['player'].split()[-1],
                    axis=1
                )

                # Position abbreviation
                from Module.chart import get_position_abbr
                df['pos_abbr'] = df['position_name'].apply(
                    get_position_abbr
                )

                display = df[[
                    'jersey_number',
                    'display_name',
                    'pos_abbr',
                    'country_name'
                ]].copy()
                display.columns = ['#', 'Player', 'Pos', 'Country']
                display = display.sort_values('#')
                st.dataframe(
                    display.set_index('#'),
                    use_container_width=True
                )
            else:
                st.info("No lineup data available.")
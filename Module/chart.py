# utils/metrics.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from Module.metrics import build_momentum, build_xg_story
from mplsoccer import Pitch, VerticalPitch
import matplotlib.pyplot as plt
from config import PITCH_COLOR, LINE_COLOR, BG_PRIMARY, TEXT_SECONDARY
from config import ACCENT_AMBER, TEXT_PRIMARY, BG_PRIMARY


POSITION_COORDS = {
    "Goalkeeper": {
        "coords": (5, 40),
        "abbr": "GK"
    },
    "Right Back": {
        "coords": (25, 68),
        "abbr": "RB"
    },
    "Right Center Back": {
        "coords": (20, 55),
        "abbr": "RCB"
    },
    "Center Back": {
        "coords": (20, 40),
        "abbr": "CB"
    },
    "Left Center Back": {
        "coords": (20, 25),
        "abbr": "LCB"
    },
    "Left Back": {
        "coords": (25, 12),
        "abbr": "LB"
    },
    "Right Wing Back": {
        "coords": (40, 72),
        "abbr": "RWB"
    },
    "Left Wing Back": {
        "coords": (40, 8),
        "abbr": "LWB"
    },
    "Right Defensive Midfield": {
        "coords": (38, 58),
        "abbr": "RDM"
    },
    "Center Defensive Midfield": {
        "coords": (38, 40),
        "abbr": "CDM"
    },
    "Left Defensive Midfield": {
        "coords": (38, 22),
        "abbr": "LDM"
    },
    "Right Midfield": {
        "coords": (55, 68),
        "abbr": "RM"
    },
    "Right Center Midfield": {
        "coords": (52, 56),
        "abbr": "RCM"
    },
    "Center Midfield": {
        "coords": (52, 40),
        "abbr": "CM"
    },
    "Left Center Midfield": {
        "coords": (52, 24),
        "abbr": "LCM"
    },
    "Left Midfield": {
        "coords": (55, 12),
        "abbr": "LM"
    },
    "Right Attacking Midfield": {
        "coords": (65, 58),
        "abbr": "RAM"
    },
    "Center Attacking Midfield": {
        "coords": (65, 40),
        "abbr": "CAM"
    },
    "Left Attacking Midfield": {
        "coords": (65, 22),
        "abbr": "LAM"
    },
    "Right Wing": {
        "coords": (78, 70),
        "abbr": "RW"
    },
    "Right Center Forward": {
        "coords": (75, 55),
        "abbr": "RCF"
    },
    "Center Forward": {
        "coords": (78, 40),
        "abbr": "CF"
    },
    "Left Center Forward": {
        "coords": (75, 25),
        "abbr": "LCF"
    },
    "Left Wing": {
        "coords": (78, 10),
        "abbr": "LW"
    },
    "Secondary Striker": {
        "coords": (68, 40),
        "abbr": "SS"
    },
    "Striker": {
        "coords": (85, 40),
        "abbr": "ST"
    },
}

def get_position_coords(position_name):
    """Returns (x, y) tuple or None if not found."""
    pos = POSITION_COORDS.get(position_name)
    return pos['coords'] if pos else None

def get_position_abbr(position_name):
    """Returns abbreviation string or the full name as fallback."""
    pos = POSITION_COORDS.get(position_name)
    return pos['abbr'] if pos else position_name


def make_pitch(vertical=False, half=False, figsize=(10, 7)):
    """Returns (fig, ax) with consistent dark theme."""
    kwargs = dict(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        goal_type='box',
        corner_arcs=True,
    )
    if vertical:
        pitch = VerticalPitch(half=half, **kwargs)
    else:
        pitch = Pitch(**kwargs)

    fig, ax = pitch.draw(figsize=figsize)
    fig.patch.set_facecolor(BG_PRIMARY)
    return pitch, fig, ax


def hex_to_rgba(hex_color, opacity=0.08):
    """Convert hex color string to rgba() for Plotly fillcolor."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'


def plot_xg_story(shots, home_team, away_team,
                  home_color="royalblue", away_color="tomato"):
    xg_data = build_xg_story(shots)
    fig     = go.Figure()

    # Map rgba fills to match line colors
    fill_colors = {
        home_team: "rgba(65, 105, 225, 0.10)",   # royalblue at 10%
        away_team: "rgba(255, 99,  71, 0.10)",   # tomato at 10%
    }
    line_colors = {
        home_team: home_color,
        away_team: away_color,
    }

    for team in [home_team, away_team]:
        if team not in xg_data:
            continue

        df    = xg_data[team]
        goals = df[df["is_goal"] == True]
        color = line_colors[team]
        fill  = fill_colors[team]

        # ── Step line ─────────────────────────────────────
        fig.add_trace(go.Scatter(
            x=df["minute"],
            y=df["cumulative_xg"],
            mode="lines",
            name=team,
            line=dict(color=color, width=2.5, shape="hv"),
            fill="tozeroy",
            fillcolor=fill,                          # ✅ clean rgba
            hovertemplate=(
                f"<b>{team}</b><br>"
                "Minute: %{x}'<br>"
                "Cumulative xG: %{y:.2f}<br>"
                "<extra></extra>"
            ),
        ))

        # ── Goal markers ──────────────────────────────────
        if len(goals):
            fig.add_trace(go.Scatter(
                x=goals["minute"],
                y=goals["cumulative_xg"],
                mode="markers",
                name=f"{team} goal",
                showlegend=False,
                marker=dict(
                    symbol="star",
                    size=14,
                    color=color,
                    line=dict(color="white", width=1)
                ),
                hovertemplate=(
                    f"<b>GOAL — {team}</b><br>"
                    "Minute: %{x}'<br>"
                    "Shot xG: %{customdata:.2f}<br>"
                    "<extra></extra>"
                ),
                customdata=goals["xg"],
            ))

    # ── Max minute for dynamic x range ────────────────────
    max_minute = max(df["minute"].max() for df in xg_data.values())

    # ── Reference lines ───────────────────────────────────
    for minute, label in [(45, "HT"), (90, "FT")]:
        fig.add_vline(
            x=minute, line_dash="dot",
            line_color="#475569", line_width=1,
            annotation_text=label,
            annotation_font_color="#475569",
            annotation_font_size=11,
        )

    # ── Layout ────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#151b23",
        font=dict(color="#e2e8f0", family="DM Sans"),
        height=360,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            title="Minute",
            range=[0, max_minute + 2],              # ✅ correct place
            tickvals=[0, 15, 30, 45, 60, 75, 90],
            gridcolor="#1e2a38",
            zeroline=False,
            color="#64748b",
        ),
        yaxis=dict(
            title="Cumulative xG",
            gridcolor="#1e2a38",
            zeroline=False,
            color="#64748b",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left",   x=0,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )

    return fig

def plot_lineup(lineup, color, flip=False):
    """
    Plots starting XI on pitch using POSITION_COORDS.
    Only receives 11 starters — subs are excluded upstream
    in get_starting_xi() by filtering to Starting XI events.
    
    flip=True mirrors x-axis for away team so they
    attack in the correct direction visually.
    """
    pitch, fig, ax = make_pitch(figsize=(8, 6))
    missing_positions = []

    for player_dict in lineup:
        position_name = player_dict.get('position_name', '')

        # ── Safe jersey number ─────────────────────────────
        jersey_raw = player_dict.get('jersey_number', 0)
        jersey = str(int(jersey_raw)) \
                 if jersey_raw and \
                 str(jersey_raw) not in ['nan', 'None'] \
                 else '?'

        # ── Resolve coordinates from position dict ─────────
        coords = get_position_coords(position_name)
        if coords is None:
            missing_positions.append(position_name)
            continue

        x, y = coords
        if flip:
            x = 120 - x

        # ── Display name ───────────────────────────────────
        nickname  = player_dict.get('player_nickname', '')
        full_name = player_dict.get('player', '')
        if nickname and str(nickname).strip() \
                not in ['', 'nan', 'None']:
            display_name = nickname
        else:
            display_name = full_name.split()[-1] \
                           if full_name else '?'

        # ── Colors ─────────────────────────────────────────
        is_gk     = position_name == 'Goalkeeper'
        dot_color = ACCENT_AMBER if is_gk else color
        txt_color = '#0e1117'    if is_gk else 'white'

        # ── Dot ───────────────────────────────────────────
        ax.scatter(
            x, y, s=550,
            color=dot_color,
            edgecolors='white',
            linewidths=1.2,
            zorder=5
        )

        # ── Jersey number ──────────────────────────────────
        ax.text(
            x, y, jersey,
            ha='center', va='center',
            color=txt_color, fontsize=8,
            fontweight='bold', zorder=6
        )

        # ── Player name below dot ──────────────────────────
        ax.text(
            x, y - 4, display_name,
            ha='center', va='top',
            color=TEXT_PRIMARY, fontsize=6.5,
            bbox=dict(
                boxstyle='round,pad=0.2',
                facecolor=BG_PRIMARY,
                edgecolor='none',
                alpha=0.75
            ),
            zorder=7
        )

    # ── Surface missing positions in chart ─────────────────
    if missing_positions:
        ax.text(
            2, 2,
            f"Missing coords: {', '.join(set(missing_positions))}",
            color='tomato', fontsize=6,
            bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                      edgecolor='none', pad=2)
        )

    return fig

def plot_shot_timeline(shots, home_team, away_team):
    """
    Compact horizontal shot timeline.
    Sits below the xG story chart as a companion visual.
    """
    home_shots = shots[shots['team_name'] == home_team].copy()
    away_shots = shots[shots['team_name'] == away_team].copy()

    outcome_style = {
        'Goal':    ('gold',       'star',    16),
        'Saved':   ('royalblue',  'circle',  10),
        'Off T':   ('tomato',     'x',        8),
        'Blocked': ('#8b949e',    'square',   8),
        'Wayward': ('#475569',    'x',        7),
    }

    fig = go.Figure()

    for team_shots, y_val, team_name in [
        (home_shots,  1,  home_team),
        (away_shots, -1,  away_team),
    ]:
        for _, shot in team_shots.iterrows():
            outcome = shot.get('outcome_name', 'Off T')
            xg      = float(shot.get('shot_statsbomb_xg', 0.05) or 0.05)
            minute  = int(shot.get('minute', 0))

            color, symbol, base_size = outcome_style.get(
                outcome, ('#8b949e', 'circle', 8)
            )
            size = base_size + xg * 30  # scale dot by xG

            fig.add_trace(go.Scatter(
                x=[minute],
                y=[y_val],
                mode='markers',
                marker=dict(
                    symbol=symbol,
                    size=size,
                    color=color,
                    line=dict(color='white', width=0.5),
                ),
                name=outcome,
                showlegend=False,
                hovertemplate=(
                    f"<b>{team_name}</b><br>"
                    f"Minute: {minute}'<br>"
                    f"xG: {xg:.2f}<br>"
                    f"Outcome: {outcome}<br>"
                    "<extra></extra>"
                ),
            ))

    # ── HT line ────────────────────────────────────────────
    fig.add_vline(
        x=45, line_dash="dot",
        line_color="#475569", line_width=1
    )

    # ── Team labels on y axis ──────────────────────────────
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#151b23",
        height=140,
        margin=dict(l=80, r=20, t=10, b=30),
        xaxis=dict(
            range=[0, 95],
            tickvals=[0, 15, 30, 45, 60, 75, 90],
            gridcolor="#1e2a38",
            zeroline=False,
            color="#64748b",
        ),
        yaxis=dict(
            tickvals=[1, -1],
            ticktext=[home_team, away_team],
            gridcolor="#1e2a38",
            zeroline=True,
            zerolinecolor="#2d3f50",
            zerolinewidth=1,
            color="#64748b",
            range=[-2, 2],
        ),
        hovermode='closest',
        showlegend=False,
    )

    # ── Manual legend ──────────────────────────────────────
    legend_items = [
        ('gold',      'star',   'Goal'),
        ('royalblue', 'circle', 'Saved'),
        ('tomato',    'x',      'Off Target'),
        ('#8b949e',   'square', 'Blocked'),
    ]
    for i, (color, symbol, label) in enumerate(legend_items):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(symbol=symbol, size=8, color=color),
            name=label,
            showlegend=True,
        ))

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom', y=1.05,
            xanchor='left',   x=0,
            font=dict(size=10, color='#94a3b8'),
            bgcolor='rgba(0,0,0,0)',
        )
    )

    return fig


def plot_momentum(events, home_team, away_team, window=3):
    """
    Bar chart style momentum — green above = home dominant,
    red below = away dominant.
    """
    df = build_momentum(events, home_team, away_team, window)

    # Split into home and away dominance
    home_momentum = df['momentum'].clip(lower=0)  # positive only
    away_momentum = df['momentum'].clip(upper=0)  # negative only

    fig = go.Figure()

    # ── Home momentum (above zero) ─────────────────────────
    fig.add_trace(go.Bar(
        x=df['minute'],
        y=home_momentum,
        name=home_team,
        marker_color='royalblue',
        marker_line_width=0,
        hovertemplate=(
            f"<b>{home_team}</b><br>"
            "Minute: %{x}'<br>"
            "Momentum: %{y:.1f}<br>"
            "<extra></extra>"
        )
    ))

    # ── Away momentum (below zero) ─────────────────────────
    fig.add_trace(go.Bar(
        x=df['minute'],
        y=away_momentum,
        name=away_team,
        marker_color='tomato',
        marker_line_width=0,
        hovertemplate=(
            f"<b>{away_team}</b><br>"
            "Minute: %{x}'<br>"
            "Momentum: %{y:.1f}<br>"
            "<extra></extra>"
        )
    ))

    # ── Goal markers ───────────────────────────────────────
    shots = events[events['outcome_name'] == 'Goal'].copy()
    for _, goal in shots.iterrows():
        is_home  = goal['team_name'] == home_team
        color    = 'royalblue' if is_home else 'tomato'
        y_pos    = 2 if is_home else -2
        player   = goal.get('player_name', '')
        minute   = int(goal['minute'])

        fig.add_annotation(
            x=minute,
            y=y_pos,
            text=f"⚽ {player} {minute}'",
            showarrow=True,
            arrowhead=2,
            arrowcolor=color,
            font=dict(color=color, size=10),
            bgcolor="#0e1117",
            bordercolor=color,
            borderwidth=1,
            borderpad=3,
        )

    # ── HT line ────────────────────────────────────────────
    fig.add_vline(
        x=45, line_dash="dot",
        line_color="#475569", line_width=1,
        annotation_text="HT",
        annotation_font_color="#475569",
        annotation_font_size=10,
    )

    # ── Zero line labels ───────────────────────────────────
    fig.add_annotation(
        x=2, y=0.3, text=home_team,
        showarrow=False,
        font=dict(color='royalblue', size=10)
    )
    fig.add_annotation(
        x=2, y=-0.3, text=away_team,
        showarrow=False,
        font=dict(color='tomato', size=10)
    )

    # ── Layout ─────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#151b23",
        font=dict(color="#e2e8f0", family="DM Sans"),
        height=280,
        barmode='relative',
        bargap=0,
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(
            title="Minute",
            range=[0, 90],
            tickvals=[0, 15, 30, 45, 60, 75, 90],
            gridcolor="#1e2a38",
            zeroline=False,
            color="#64748b",
        ),
        yaxis=dict(
            title="Momentum",
            gridcolor="#1e2a38",
            zeroline=True,
            zerolinecolor="#2d3f50",
            zerolinewidth=2,
            color="#64748b",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        hovermode="x unified",
    )

    return fig


def plot_final_third_entries(passes, carries, color):
    """
    Shows all passes and carries that entered the final third (x > 80).
    Passes = arrows, Carries = arrows in different shade.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    # Final third entries via pass
    # Pass starts outside final third, ends inside
    ft_passes = passes[
        (passes['x'] < 80) &
        (passes['end_x'] >= 80)
    ].copy() if 'end_x' in passes.columns else pd.DataFrame()

    # Final third entries via carry
    ft_carries = carries[
        (carries['x'] < 80) &
        (carries['end_x'] >= 80)
    ].copy() if 'end_x' in carries.columns else pd.DataFrame()

    # Draw final third line
    ax.axvline(
        x=80, color='#f59e0b',
        linewidth=1.2, linestyle='--',
        alpha=0.6, zorder=3
    )
    ax.text(
        81, 2, 'Final Third',
        color='#f59e0b', fontsize=7, alpha=0.8
    )

    # ── Pass entries ───────────────────────────────────────
    if not ft_passes.empty:
        pitch.arrows(
            ft_passes['x'], ft_passes['y'],
            ft_passes['end_x'], ft_passes['end_y'],
            ax=ax,
            color=color,
            alpha=0.5,
            width=1.5,
            headwidth=4,
            headlength=4,
            zorder=4,
            label='Pass'
        )

    # ── Carry entries ──────────────────────────────────────
    if not ft_carries.empty:
        pitch.arrows(
            ft_carries['x'], ft_carries['y'],
            ft_carries['end_x'], ft_carries['end_y'],
            ax=ax,
            color='gold',
            alpha=0.7,
            width=1.5,
            headwidth=4,
            headlength=4,
            zorder=5,
            label='Carry'
        )

    # ── KDE of entry endpoints ─────────────────────────────
    all_end_x = []
    all_end_y = []

    if not ft_passes.empty:
        all_end_x.extend(ft_passes['end_x'].tolist())
        all_end_y.extend(ft_passes['end_y'].tolist())
    if not ft_carries.empty:
        all_end_x.extend(ft_carries['end_x'].tolist())
        all_end_y.extend(ft_carries['end_y'].tolist())

    if len(all_end_x) > 5:
        import pandas as pd
        kde_df = pd.DataFrame({'x': all_end_x, 'y': all_end_y})
        pitch.kdeplot(
            kde_df['x'], kde_df['y'],
            ax=ax,
            cmap='YlOrRd',
            fill=True,
            alpha=0.3,
            levels=8,
            thresh=0.1,
            zorder=2
        )

    # ── Stats annotation ───────────────────────────────────
    ax.text(
        2, 76,
        f"Pass entries: {len(ft_passes)}",
        color=color, fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )
    ax.text(
        2, 71,
        f"Carry entries: {len(ft_carries)}",
        color='gold', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_box_entries(passes, carries, color):
    """
    Shows all passes and carries that entered the penalty box.
    Box = x > 102, y between 18 and 62 (StatsBomb coords).
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    def in_box(end_x, end_y):
        return (end_x >= 102) & (end_y >= 18) & (end_y <= 62)

    # Box entries via pass
    box_passes = passes[
        (passes['x'] < 102) &
        in_box(passes['end_x'], passes['end_y'])
    ].copy() if 'end_x' in passes.columns else pd.DataFrame()

    # Box entries via carry
    box_carries = carries[
        (carries['x'] < 102) &
        in_box(carries['end_x'], carries['end_y'])
    ].copy() if 'end_x' in carries.columns else pd.DataFrame()

    # ── Pass entries into box ──────────────────────────────
    if not box_passes.empty:
        pitch.arrows(
            box_passes['x'], box_passes['y'],
            box_passes['end_x'], box_passes['end_y'],
            ax=ax,
            color=color,
            alpha=0.6,
            width=1.8,
            headwidth=5,
            headlength=4,
            zorder=4
        )

    # ── Carry entries into box ─────────────────────────────
    if not box_carries.empty:
        pitch.arrows(
            box_carries['x'], box_carries['y'],
            box_carries['end_x'], box_carries['end_y'],
            ax=ax,
            color='gold',
            alpha=0.8,
            width=1.8,
            headwidth=5,
            headlength=4,
            zorder=5
        )

    # ── Start locations as dots ────────────────────────────
    all_start_x = []
    all_start_y = []

    if not box_passes.empty:
        all_start_x.extend(box_passes['x'].tolist())
        all_start_y.extend(box_passes['y'].tolist())
    if not box_carries.empty:
        all_start_x.extend(box_carries['x'].tolist())
        all_start_y.extend(box_carries['y'].tolist())

    if all_start_x:
        pitch.scatter(
            all_start_x, all_start_y,
            s=30, color='white',
            alpha=0.3, ax=ax, zorder=3
        )

    # ── Stats annotation ───────────────────────────────────
    total = len(box_passes) + len(box_carries)
    ax.text(
        2, 76,
        f"Pass entries: {len(box_passes)}",
        color=color, fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )
    ax.text(
        2, 71,
        f"Carry entries: {len(box_carries)}",
        color='gold', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )
    ax.text(
        2, 66,
        f"Total: {total}",
        color='white', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_shot_map(shots, team, color):
    """
    Vertical half-pitch shot map.
    Size = xG, color = outcome.
    """
    vp = VerticalPitch(
        pitch_type='statsbomb',
        half=True,
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
    )
    fig, ax = vp.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    if shots.empty:
        ax.text(40, 60, 'No shots',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    outcome_style = {
        'Goal':    ('gold',      250),
        'Saved':   (color,       120),
        'Off T':   ('#f97316',    80),
        'Blocked': ('#8b949e',    70),
        'Wayward': ('#475569',    60),
    }

    for _, shot in shots.iterrows():
        outcome  = shot.get('outcome_name', 'Off T')
        xg       = float(shot.get('shot_statsbomb_xg', 0.05) or 0.05)
        dot_color, base_size = outcome_style.get(
            outcome, ('#8b949e', 70)
        )
        size = base_size + xg * 400

        vp.scatter(
            shot['x'], shot['y'],
            s=size, color=dot_color,
            edgecolors='white', linewidths=0.5,
            alpha=0.85, ax=ax, zorder=5
        )

    # ── xG total annotation ────────────────────────────────
    total_xg = shots['shot_statsbomb_xg'].sum() \
               if 'shot_statsbomb_xg' in shots.columns else 0
    goals    = len(shots[shots['outcome_name'] == 'Goal'])

    ax.text(
        40, 82,
        f"Goals: {goals}  |  xG: {total_xg:.2f}",
        ha='center', color='white',
        fontsize=9, fontweight='bold',
    )

    # ── Manual legend ──────────────────────────────────────
    legend_elements = [
        plt.scatter([], [], s=80,  color='gold',    label='Goal',    edgecolors='white', linewidths=0.5),
        plt.scatter([], [], s=60,  color=color,     label='Saved',   edgecolors='white', linewidths=0.5),
        plt.scatter([], [], s=50,  color='#f97316', label='Off T',   edgecolors='white', linewidths=0.5),
        plt.scatter([], [], s=50,  color='#8b949e', label='Blocked', edgecolors='white', linewidths=0.5),
    ]
    ax.legend(
        handles=legend_elements,
        loc='lower left', fontsize=7,
        facecolor=BG_PRIMARY, labelcolor='white',
        edgecolor='none', markerscale=1
    )

    return fig


def plot_carry_map(carries, team, color):
    """
    Progressive carries — arrows showing forward ball progression.
    Progressive = carry gaining more than 5m toward goal.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    if carries.empty:
        ax.text(60, 40, 'No carry data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    # Progressive carries only
    prog = carries[
        (carries['end_x'] - carries['x'] > 5)
    ].copy()

    if prog.empty:
        ax.text(60, 40, 'No progressive carries',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    pitch.arrows(
        prog['x'], prog['y'],
        prog['end_x'], prog['end_y'],
        ax=ax,
        color=color,
        alpha=0.5,
        width=1.5,
        headwidth=4,
        headlength=4,
        zorder=4
    )

    # ── Carry into box highlight ───────────────────────────
    box_carries = prog[prog['end_x'] > 102]
    if len(box_carries):
        pitch.arrows(
            box_carries['x'], box_carries['y'],
            box_carries['end_x'], box_carries['end_y'],
            ax=ax,
            color='gold',
            alpha=0.9,
            width=2,
            headwidth=5,
            headlength=5,
            zorder=5
        )

    ax.text(
        2, 76,
        f"Progressive: {len(prog)}",
        color='white', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )
    ax.text(
        2, 72,
        f"Into box: {len(box_carries)}",
        color='gold', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_chance_creation_zones(passes, color):
    """
    KDE heatmap of where key passes end up —
    shows which zones chances are being created from.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    # Key passes = passes ending in final third
    key_passes = passes[passes['end_x'] > 80].copy()

    if len(key_passes) < 5:
        ax.text(60, 40, 'Not enough data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    pitch.kdeplot(
        key_passes['end_x'],
        key_passes['end_y'],
        ax=ax,
        cmap='YlOrRd',
        fill=True,
        alpha=0.65,
        levels=10,
        thresh=0.1,
    )

    # Overlay the actual pass endpoints as dots
    pitch.scatter(
        key_passes['end_x'],
        key_passes['end_y'],
        s=15,
        color='white',
        alpha=0.3,
        ax=ax,
        zorder=4
    )

    ax.text(
        60, 77,
        f"Passes into final third: {len(key_passes)}",
        ha='center', color='white', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig

def plot_pass_network(passes, team, color, starting_xi=None):
    """
    Pass network showing connections between players.
    Thicker lines = more passes between that pair.
    Node position = average position during the match.
    
    starting_xi: optional list of starter dicts — if provided,
    filters to starters only for a cleaner shape view.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    # Successful passes only
    sp = passes[passes['outcome_name'].isna()].copy()

    if sp.empty:
        ax.text(60, 40, 'No pass data available',
                ha='center', va='center',
                color=TEXT_SECONDARY, fontsize=10)
        return fig

    # ── Filter to starters only if provided ───────────────
    if starting_xi:
        starter_names = [p['player'] for p in starting_xi]
        sp = sp[sp['player_name'].isin(starter_names)]

    # ── Average position per player ────────────────────────
    avg_pos = sp.groupby('player_name')[['x', 'y']].mean()

    if avg_pos.empty:
        ax.text(60, 40, 'Not enough pass data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    # ── Pass count between player pairs ───────────────────
    recipient_col = 'pass_recipient_name' \
                    if 'pass_recipient_name' in sp.columns \
                    else 'pass_recipient'

    if recipient_col not in sp.columns:
        ax.text(60, 40, 'Recipient column not found',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    pass_counts = sp.groupby(
        ['player_name', recipient_col]
    ).size().reset_index(name='count')

    # ── Draw connections ───────────────────────────────────
    for _, row in pass_counts[pass_counts['count'] > 3].iterrows():
        p1 = row['player_name']
        p2 = row[recipient_col]

        if p1 in avg_pos.index and p2 in avg_pos.index:
            x_vals = [avg_pos.loc[p1, 'x'], avg_pos.loc[p2, 'x']]
            y_vals = [avg_pos.loc[p1, 'y'], avg_pos.loc[p2, 'y']]

            alpha     = min(row['count'] / 25, 0.9)
            linewidth = min(row['count'] / 6,  4.0)

            ax.plot(x_vals, y_vals,
                    color=color, alpha=alpha,
                    linewidth=linewidth, zorder=3)

    # ── Draw nodes ─────────────────────────────────────────
    pitch.scatter(
        avg_pos['x'], avg_pos['y'],
        s=300, color=color,
        edgecolors='white', linewidths=1.2,
        ax=ax, zorder=5
    )

    # ── Player surnames ────────────────────────────────────
    for player, pos in avg_pos.iterrows():
        surname = player.split()[-1]
        ax.annotate(
            surname,
            (pos['x'], pos['y']),
            xytext=(0, 7), textcoords='offset points',
            fontsize=6, color='white',
            ha='center', va='bottom', zorder=6
        )

    return fig


def plot_average_positions(events, team, color,
                            starting_xi=None):
    """
    Average position map showing where each player
    actually operated during the match.

    starting_xi: optional list of starter dicts — filters
    to starters only so subs don't distort the shape view.
    Dot size scales with number of touches.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    # ── Check actual event type column values ──────────────
    # Sbopen uses 'type_name' — verify touch type names
    touch_types = [
        'Pass', 'Carry', 'Shot', 'Dribble',
        'Ball Receipt*', 'Clearance', 'Pressure'
    ]

    # Be safe — filter to whatever matches
    available_types = events['type_name'].unique()
    valid_touch_types = [t for t in touch_types
                         if t in available_types]

    touches = events[
        (events['type_name'].isin(valid_touch_types)) &
        (events['team_name'] == team)
    ].copy()

    # ── Filter to starters only if provided ───────────────
    if starting_xi:
        starter_names = [p['player'] for p in starting_xi]
        touches = touches[
            touches['player_name'].isin(starter_names)
        ]

    if touches.empty:
        ax.text(60, 40, 'No touch data available',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    # ── Average position + touch count ────────────────────
    avg_pos     = touches.groupby('player_name')[['x', 'y']].mean()
    touch_count = touches.groupby('player_name').size()
    max_touches = touch_count.max()

    for player, pos in avg_pos.iterrows():
        n_touches = touch_count.get(player, 1)
        size      = 200 + (n_touches / max_touches) * 400

        ax.scatter(
            pos['x'], pos['y'],
            s=size, color=color,
            edgecolors='white', linewidths=1.2,
            alpha=0.85, zorder=5
        )

        surname = player.split()[-1]
        ax.text(
            pos['x'], pos['y'] - 4, surname,
            ha='center', va='top',
            color='white', fontsize=6.5,
            bbox=dict(
                boxstyle='round,pad=0.2',
                facecolor=BG_PRIMARY,
                edgecolor='none', alpha=0.75
            ),
            zorder=6
        )

    ax.text(
        2, 76, "Dot size = number of touches",
        color=TEXT_SECONDARY, fontsize=7,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_substitution_timeline(events, match_row):
    """
    Horizontal timeline of substitutions for both teams.
    ⬆️ Green triangle = player coming on.
    ⬇️ Red triangle   = player going off.
    Handles multiple subs at the same minute with y-jitter.
    """
    import plotly.graph_objects as go

    home = match_row["home_team_name"]
    away = match_row["away_team_name"]

    subs = events[events['type_name'] == 'Substitution'].copy()

    if subs.empty:
        return None

    fig = go.Figure()
    team_y     = {home:  1, away: -1}
    team_color = {home: 'royalblue', away: 'tomato'}

    # Track sub count per team per minute for jitter
    sub_count = {}

    for _, sub in subs.iterrows():
        team   = sub['team_name']
        minute = int(sub['minute'])

        player_out = sub.get('player_name', 'Unknown')

        # Safe extraction — Sbopen sometimes returns dict
        player_in_raw = sub.get('substitution_replacement',
                                'Unknown')
        player_in = player_in_raw['name'] \
                    if isinstance(player_in_raw, dict) \
                    else str(player_in_raw)

        # Y jitter for same-minute subs
        key    = (team, minute)
        jitter = sub_count.get(key, 0) * 0.15
        sub_count[key] = sub_count.get(key, 0) + 1

        y_base = team_y.get(team, 0)
        color  = team_color.get(team, '#8b949e')

        # Player coming ON
        fig.add_trace(go.Scatter(
            x=[minute], y=[y_base + 0.2 + jitter],
            mode='markers+text',
            marker=dict(symbol='triangle-up', size=12,
                        color='#3fb950',
                        line=dict(color='white', width=0.5)),
            text=[player_in],
            textposition='top center',
            textfont=dict(size=8, color='#3fb950'),
            showlegend=False,
            hovertemplate=(
                f"<b>⬆️ {player_in}</b><br>"
                f"Team: {team}<br>"
                f"Minute: {minute}'<br>"
                "<extra></extra>"
            )
        ))

        # Player going OFF
        fig.add_trace(go.Scatter(
            x=[minute], y=[y_base - 0.2 - jitter],
            mode='markers+text',
            marker=dict(symbol='triangle-down', size=12,
                        color='tomato',
                        line=dict(color='white', width=0.5)),
            text=[player_out],
            textposition='bottom center',
            textfont=dict(size=8, color='tomato'),
            showlegend=False,
            hovertemplate=(
                f"<b>⬇️ {player_out}</b><br>"
                f"Team: {team}<br>"
                f"Minute: {minute}'<br>"
                "<extra></extra>"
            )
        ))

        # Connector line
        fig.add_shape(
            type='line',
            x0=minute, x1=minute,
            y0=y_base - 0.2 - jitter,
            y1=y_base + 0.2 + jitter,
            line=dict(color=color, width=1, dash='dot')
        )

    # ── HT line ────────────────────────────────────────────
    fig.add_vline(
        x=45, line_dash='dot',
        line_color='#475569', line_width=1,
        annotation_text='HT',
        annotation_font_color='#475569',
        annotation_font_size=10,
    )

    # ── Team labels ────────────────────────────────────────
    for team, y_val in team_y.items():
        fig.add_annotation(
            x=2, y=y_val,
            text=f"<b>{team}</b>",
            showarrow=False,
            font=dict(color=team_color[team], size=11),
            xanchor='left'
        )

    fig.update_layout(
        paper_bgcolor='#0e1117',
        plot_bgcolor='#151b23',
        font=dict(color='#e2e8f0', family='DM Sans'),
        height=320,
        margin=dict(l=20, r=20, t=30, b=30),
        xaxis=dict(
            title='Minute',
            range=[0, 95],
            tickvals=[0, 15, 30, 45, 60, 75, 90],
            gridcolor='#1e2a38',
            zeroline=False,
            color='#64748b',
        ),
        yaxis=dict(
            range=[-1.8, 1.8],
            tickvals=[1, -1],
            ticktext=[home, away],
            gridcolor='#1e2a38',
            zeroline=True,
            zerolinecolor='#2d3f50',
            zerolinewidth=2,
            color='#64748b',
        ),
        hovermode='closest',
        showlegend=False,
    )

    return fig


def plot_formation_timeline(events, match_row):
    """
    Timeline of formation changes for both teams.
    Starting formation shown at minute 0.
    Tactical shifts shown as dashed vertical lines.
    """
    import plotly.graph_objects as go
    import pandas as pd

    home = match_row["home_team_name"]
    away = match_row["away_team_name"]

    xi_events = events[
        events['type_name'] == 'Starting XI'
    ].copy()
    shift_events = events[
        events['type_name'] == 'Tactical Shift'
    ].copy()

    formation_events = pd.concat(
        [xi_events, shift_events], ignore_index=True
    ).sort_values('minute')

    if formation_events.empty:
        return None

    fig = go.Figure()

    team_y     = {home:  1, away: -1}
    team_color = {home: 'royalblue', away: 'tomato'}

    for team in [home, away]:
        team_formations = formation_events[
            formation_events['team_name'] == team
        ].copy()

        if team_formations.empty:
            continue

        y_val = team_y[team]
        color = team_color[team]

        for i, (_, row) in enumerate(
            team_formations.iterrows()
        ):
            minute = int(row['minute'])

            # Safe formation extraction
            formation = str(row['tactics_formation']) \
                        if 'tactics_formation' in row.index \
                        and pd.notna(row.get('tactics_formation')) \
                        else '?'

            # Formation label box
            fig.add_annotation(
                x=minute + 1, y=y_val,
                text=f"<b>{formation}</b>",
                showarrow=False,
                font=dict(color=color, size=12),
                xanchor='left',
                bgcolor='#151b23',
                bordercolor=color,
                borderwidth=1,
                borderpad=4,
            )

            # Shift marker — only for changes, not start
            if i > 0:
                fig.add_vline(
                    x=minute, line_dash='dash',
                    line_color=color,
                    line_width=1, opacity=0.5,
                )
                fig.add_annotation(
                    x=minute,
                    y=y_val + (0.3 if y_val > 0 else -0.3),
                    text=f"{minute}'",
                    showarrow=False,
                    font=dict(color=color, size=9),
                )

    # ── HT + team labels ───────────────────────────────────
    fig.add_vline(
        x=45, line_dash='dot',
        line_color='#475569', line_width=1,
        annotation_text='HT',
        annotation_font_color='#475569',
        annotation_font_size=10,
    )

    for team, y_val in team_y.items():
        fig.add_annotation(
            x=1, y=y_val + (0.4 if y_val > 0 else -0.4),
            text=f"<b>{team}</b>",
            showarrow=False,
            font=dict(color=team_color[team], size=11),
            xanchor='left'
        )

    fig.update_layout(
        paper_bgcolor='#0e1117',
        plot_bgcolor='#151b23',
        font=dict(color='#e2e8f0', family='DM Sans'),
        height=280,
        margin=dict(l=20, r=20, t=30, b=30),
        xaxis=dict(
            title='Minute',
            range=[0, 95],
            tickvals=[0, 15, 30, 45, 60, 75, 90],
            gridcolor='#1e2a38',
            zeroline=False,
            color='#64748b',
        ),
        yaxis=dict(
            range=[-2, 2],
            tickvals=[1, -1],
            ticktext=[home, away],
            gridcolor='#1e2a38',
            zeroline=True,
            zerolinecolor='#2d3f50',
            zerolinewidth=2,
            color='#64748b',
        ),
        showlegend=False,
        hovermode='closest',
    )

    return fig

def plot_pressure_heatmap(pressures, team, color):
    """
    Full pitch KDE heatmap of where the team applied pressure.

    High concentration in opponent half = high press.
    Low concentration in own half = sitting deep.
    The shape of the heatmap reveals the pressing system —
    man-oriented press looks different from zonal press.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    pressures = pressures[pressures['team_name'] == team].copy()

    if pressures.empty or len(pressures) < 5:
        ax.text(60, 40, 'Not enough pressure data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    pitch.kdeplot(
        pressures['x'], pressures['y'],
        ax=ax,
        cmap='Reds',
        fill=True,
        alpha=0.7,
        levels=12,
        thresh=0.05,
        zorder=2
    )

    # Overlay raw pressure dots lightly
    pitch.scatter(
        pressures['x'], pressures['y'],
        s=8, color='white', alpha=0.15,
        ax=ax, zorder=3
    )

    # Midfield line for reference
    ax.axvline(
        x=60, color='#f59e0b',
        linewidth=1, linestyle='--',
        alpha=0.4, zorder=4
    )

    ax.text(
        2, 76,
        f"Total pressures: {len(pressures)}",
        color='white', fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_high_press_map(pressures, team, color):
    """
    Shows only pressures applied in the opponent's half (x > 60).
    Reveals WHERE in the opponent's half the team pressed —
    wide channels vs central vs high up near their box.

    A team that presses high and centrally is trying to
    force the opponent into wide areas or long balls.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    high_press = pressures[(pressures['x'] > 60) & (pressures['team_name'] == team)].copy()

    if len(high_press) < 5:
        ax.text(60, 40, 'Limited high press data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    pitch.kdeplot(
        high_press['x'], high_press['y'],
        ax=ax,
        cmap='Blues',
        fill=True,
        alpha=0.7,
        levels=10,
        thresh=0.05,
        zorder=2
    )

    pitch.scatter(
        high_press['x'], high_press['y'],
        s=15, color=color, alpha=0.4,
        edgecolors='none', ax=ax, zorder=3
    )

    # High press zone line
    ax.axvline(
        x=60, color='#f59e0b',
        linewidth=1.2, linestyle='--',
        alpha=0.6, zorder=4
    )
    ax.text(
        61, 2, 'Press Zone',
        color='#f59e0b', fontsize=7, alpha=0.8
    )

    pct_high = round(len(high_press) / len(pressures) * 100, 1) \
               if len(pressures) else 0

    ax.text(
        2, 76,
        f"High pressures: {len(high_press)} ({pct_high}%)",
        color=color, fontsize=8,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_defensive_actions_map(def_actions, team, color):
    """
    All defensive actions plotted as colored dots by type.

    Tackle      = blue circle
    Interception= green circle
    Clearance   = orange circle
    Block       = grey circle
    Ball Recovery = purple circle

    Clustering pattern tells the story:
    - Actions concentrated deep = reactive defending
    - Actions spread high = proactive, aggressive shape
    - Actions in wide areas = being exposed out wide
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    def_actions = def_actions[def_actions['team_name'] == team].copy()

    if def_actions.empty:
        ax.text(60, 40, 'No defensive actions',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    action_styles = {
        'Tackle':        ('royalblue', 'o',  70, 'Tackle'),
        'Interception':  ('#3fb950',   'o',  70, 'Interception'),
        'Clearance':     ('#f59e0b',   's',  60, 'Clearance'),
        'Block':         ('#8b949e',   's',  55, 'Block'),
        'Ball Recovery': ('#a371f7',   '^',  65, 'Recovery'),
    }

    for action_type, (clr, marker, size, label) in \
            action_styles.items():
        subset = def_actions[def_actions['type_name'] == action_type]
        if subset.empty:
            continue
        pitch.scatter(
            subset['x'], subset['y'],
            s=size, color=clr,
            marker=marker,
            edgecolors='white', linewidths=0.3,
            alpha=0.8, ax=ax, zorder=5,
            label=label
        )

    ax.legend(
        loc='lower right',
        facecolor=BG_PRIMARY,
        labelcolor='white',
        fontsize=7,
        edgecolor='none',
        markerscale=1
    )

    return fig


def plot_recovery_map(def_actions, color):
    """
    Ball recovery locations — where did the team win
    the ball back after losing possession?

    High recoveries (x > 60) = effective counterpress.
    Low recoveries (x < 40) = defending deep, winning
    ball in own territory.

    Combined with PPDA this gives the full pressing picture —
    PPDA tells you HOW HARD you pressed, recovery map tells
    you WHERE you won the ball.
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    recoveries = def_actions[def_actions['type_name'] == 'Ball Recovery'].copy()

    if recoveries.empty:
        ax.text(60, 40, 'No recovery data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    # Color by zone — high recovery = brighter
    recovery_colors = recoveries['x'].apply(
        lambda x: '#3fb950' if x > 60   # opponent half
                  else color if x > 40  # midfield
                  else '#f97316'         # own half
    )

    pitch.scatter(
        recoveries['x'], recoveries['y'],
        s=80, color=recovery_colors,
        edgecolors='white', linewidths=0.5,
        alpha=0.8, ax=ax, zorder=5
    )

    # Zone reference lines
    for x_val, label in [(40, 'Mid'), (60, 'Opp Half')]:
        ax.axvline(
            x=x_val, color='#475569',
            linewidth=1, linestyle='--', alpha=0.4
        )
        ax.text(x_val + 1, 2, label,
                color='#475569', fontsize=6)

    # Zone counts
    high_rec = len(recoveries[recoveries['x'] > 60])
    mid_rec  = len(recoveries[
        (recoveries['x'] > 40) & (recoveries['x'] <= 60)
    ])
    low_rec  = len(recoveries[recoveries['x'] <= 40])

    ax.text(
        2, 76,
        f"Own half: {low_rec}  Mid: {mid_rec}  Opp: {high_rec}",
        color='white', fontsize=7,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.7,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_shots_allowed(events, team, color):
    """
    Shot map of what the OPPONENT created against us.

    This is the defensive vulnerability map —
    large dots near the centre = opponent got high
    quality chances. Gold stars = goals conceded.

    Coaches use this to identify:
    - Which zones are we being exposed in?
    - Are we conceding chances from wide or central?
    - What quality of chances are we allowing?
    """
    vp = VerticalPitch(
        pitch_type='statsbomb',
        half=True,
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
    )
    fig, ax = vp.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    # Shots BY THE OPPONENT (against selected team)
    opponent_shots = events[
        (events['type_name'] == 'Shot') &
        (events['team_name'] != team)
    ].copy()

    if opponent_shots.empty:
        ax.text(40, 60, 'No shots allowed',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    outcome_style = {
        'Goal':    ('gold',    250),
        'Saved':   (color, 120),
        'Off T':   ('#f97316',  70),
        'Blocked': ('#475569',  60),
        'Wayward': ('#8b949e',  50),
    }

    for _, shot in opponent_shots.iterrows():
        outcome  = shot.get('outcome_name', 'Off T')
        xg       = float(shot.get('shot_statsbomb_xg', 0.05) or 0.05)
        dot_color, base_size = outcome_style.get(
            outcome, ('#8b949e', 70)
        )
        size = base_size + xg * 400

        vp.scatter(
            shot['x'], shot['y'],
            s=size, color=dot_color,
            edgecolors='white', linewidths=0.5,
            alpha=0.85, ax=ax, zorder=5
        )

    # Stats
    goals_allowed = len(opponent_shots[
        opponent_shots['outcome_name'] == 'Goal'
    ])
    xg_allowed = opponent_shots['shot_statsbomb_xg'].sum() \
                 if 'shot_statsbomb_xg' in opponent_shots.columns \
                 else 0

    ax.text(
        40, 82,
        f"Goals allowed: {goals_allowed}  |  "
        f"xG allowed: {xg_allowed:.2f}",
        ha='center', color='white',
        fontsize=9, fontweight='bold',
    )

    return fig


def plot_tackle_interception_map(tackles, interceptions, color):
    """
    Tackles and interceptions only — the ball-winning actions.

    These are the moments the team actively won the ball.
    Clustering tells you:
    - High clustering = winning ball in dangerous areas
    - Wide clustering = being exposed in wide channels
    - Central clustering = good central press triggers

    Different from the full defensive actions map which
    includes clearances and blocks (reactive actions).
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    if tackles.empty and interceptions.empty:
        ax.text(60, 40, 'No tackle/interception data',
                ha='center', color=TEXT_SECONDARY, fontsize=10)
        return fig

    if not tackles.empty:
        pitch.scatter(
            tackles['x'], tackles['y'],
            s=80, color='royalblue',
            edgecolors='white', linewidths=0.5,
            alpha=0.8, ax=ax, zorder=5,
            label=f"Tackles ({len(tackles)})"
        )

    if not interceptions.empty:
        pitch.scatter(
            interceptions['x'], interceptions['y'],
            s=80, color='#3fb950',
            marker='^',
            edgecolors='white', linewidths=0.5,
            alpha=0.8, ax=ax, zorder=5,
            label=f"Interceptions ({len(interceptions)})"
        )

    # KDE if enough data
    combined = pd.concat([tackles, interceptions])
    if len(combined) > 10:
        pitch.kdeplot(
            combined['x'], combined['y'],
            ax=ax,
            cmap='Greens',
            fill=True,
            alpha=0.2,
            levels=6,
            thresh=0.1,
            zorder=2
        )

    ax.legend(
        loc='lower right',
        facecolor=BG_PRIMARY,
        labelcolor='white',
        fontsize=7,
        edgecolor='none'
    )

    return fig

def plot_counter_attack_map(df_counters, color):
    """
    Shows where each counter-attack started and
    how far it progressed.

    Each arrow = one counter possession.
    Start = where 'From Counter' possession began.
    End   = furthest x reached in that possession.

    Gold star = counter led to goal.
    Gold arrow = counter led to shot.
    Team color = no shot.
    """
    from mplsoccer import Pitch

    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(10, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    if df_counters.empty:
        ax.text(60, 40, 'No counter-attacks detected',
                ha='center', va='center',
                color=TEXT_SECONDARY, fontsize=10)
        return fig

    for _, c in df_counters.iterrows():
        start_x = c['start_x']
        start_y = c['start_y']
        end_x   = min(c['max_x'], 120)

        if c['led_to_goal']:
            arrow_color = 'gold'
            alpha       = 1.0
            lw          = 2.5
        elif c['led_to_shot']:
            arrow_color = '#f59e0b'
            alpha       = 0.8
            lw          = 2.0
        else:
            arrow_color = color
            alpha       = 0.35
            lw          = 1.2

        # Arrow from start to furthest point
        ax.annotate(
            '',
            xy=(end_x, start_y),
            xytext=(start_x, start_y),
            arrowprops=dict(
                arrowstyle='->',
                color=arrow_color,
                lw=lw,
                alpha=alpha,
                mutation_scale=12,
            )
        )

        # Start dot
        ax.scatter(
            start_x, start_y,
            s=40, color=arrow_color,
            alpha=alpha, zorder=5,
            edgecolors='white', linewidths=0.4
        )

        # Goal marker
        if c['led_to_goal']:
            ax.scatter(
                end_x, start_y,
                s=150, marker='*',
                color='gold', zorder=6,
                edgecolors='white', linewidths=0.5
            )

    # Zone reference lines
    for x_val, label in [(40, 'Mid'), (60, "Opp Half"), (80, "Final Third")]:
        ax.axvline(
            x=x_val, color='#475569',
            linewidth=0.8, linestyle='--', alpha=0.4
        )
        ax.text(x_val + 0.5, 1, label,
                color='#475569', fontsize=5.5, alpha=0.7)

    # Legend
    from matplotlib.lines import Line2D
    legend = [
        Line2D([0], [0], color='gold',   lw=2, label='Led to Goal'),
        Line2D([0], [0], color='#f59e0b', lw=2, label='Led to Shot'),
        Line2D([0], [0], color=color,    lw=1.5,
               alpha=0.5, label='No Shot'),
    ]
    ax.legend(
        handles=legend,
        loc='upper left', fontsize=7,
        facecolor=BG_PRIMARY,
        labelcolor='white',
        edgecolor='none'
    )

    ax.text(
        2, 76,
        f"Counters: {len(df_counters)}  "
        f"Shots: {df_counters['led_to_shot'].sum()}  "
        f"Goals: {df_counters['led_to_goal'].sum()}  "
        f"xG: {df_counters['xg'].sum():.2f}",
        color='white', fontsize=7.5,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.75,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_opp_counter_map(df_opp, color):
    """
    Shows where opponent counter-attacks started —
    the team's defensive transition vulnerability map.

    Red = led to shot against us.
    Red star = goal conceded from counter.
    Dim = counter that didn't result in shot.
    """
    from mplsoccer import Pitch

    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.2,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(10, 6))
    fig.patch.set_facecolor(BG_PRIMARY)

    if df_opp.empty:
        ax.text(60, 40, 'No opponent counter-attacks',
                ha='center', va='center',
                color=TEXT_SECONDARY, fontsize=10)
        return fig

    safe   = df_opp[~df_opp['led_to_shot']]
    danger = df_opp[df_opp['led_to_shot']]
    goals  = df_opp[df_opp['led_to_goal']]

    # Safe counters — dim
    if not safe.empty:
        pitch.scatter(
            safe['start_x'], safe['start_y'],
            s=60, color=color,
            edgecolors='none',
            alpha=0.2, ax=ax, zorder=4
        )

    # Dangerous counters — bright red
    if not danger.empty:
        pitch.scatter(
            danger['start_x'], danger['start_y'],
            s=100, color='tomato',
            edgecolors='white', linewidths=0.5,
            alpha=0.85, ax=ax, zorder=5
        )

    # Goals conceded — gold star
    if not goals.empty:
        pitch.scatter(
            goals['start_x'], goals['start_y'],
            s=200, color='gold',
            marker='*',
            edgecolors='white', linewidths=0.5,
            alpha=1.0, ax=ax, zorder=6
        )

    ax.text(
        2, 76,
        f"🔴 Opp counters: {len(df_opp)}  "
        f"Led to shot: {len(danger)}  "
        f"Goals conceded: {len(goals)}  "
        f"xG conceded: {df_opp['xg_conceded'].sum():.2f}",
        color='white', fontsize=7.5,
        bbox=dict(facecolor=BG_PRIMARY, alpha=0.75,
                  edgecolor='none', pad=3)
    )

    return fig


def plot_counter_timeline(df_counters, df_opp, home_team,
                           away_team, team, color):
    """
    Timeline showing when counter-attacks happened
    for both teams across the match.

    Own counters above the line.
    Opponent counters below the line.
    Height = xG of that counter.
    Gold = led to goal.
    """
    import plotly.graph_objects as go

    fig = go.Figure()

    opponent = away_team if team == home_team else home_team

    # ── Own counters (above zero) ──────────────────────────
    if not df_counters.empty:
        for _, c in df_counters.iterrows():
            dot_color = 'gold' if c['led_to_goal'] \
                        else '#f59e0b' if c['led_to_shot'] \
                        else color
            size = 10 + c['xg'] * 40

            fig.add_trace(go.Scatter(
                x=[c['minute']],
                y=[max(c['xg'], 0.05)],
                mode='markers',
                marker=dict(
                    size=size,
                    color=dot_color,
                    line=dict(color='white', width=0.5),
                    symbol='star' if c['led_to_goal']
                            else 'circle'
                ),
                name=team,
                showlegend=False,
                hovertemplate=(
                    f"<b>{team} Counter</b><br>"
                    f"Minute: {int(c['minute'])}'<br>"
                    f"xG: {c['xg']:.2f}<br>"
                    f"Shots: {int(c['n_shots'])}<br>"
                    f"Distance: {c['distance_gained']:.0f}m<br>"
                    "<extra></extra>"
                )
            ))

    # ── Opponent counters (below zero) ─────────────────────
    if not df_opp.empty:
        for _, c in df_opp.iterrows():
            dot_color = 'gold' if c['led_to_goal'] \
                        else 'tomato' if c['led_to_shot'] \
                        else '#475569'
            size = 10 + c['xg_conceded'] * 40

            fig.add_trace(go.Scatter(
                x=[c['minute']],
                y=[-max(c['xg_conceded'], 0.05)],
                mode='markers',
                marker=dict(
                    size=size,
                    color=dot_color,
                    line=dict(color='white', width=0.5),
                    symbol='star' if c['led_to_goal']
                            else 'circle'
                ),
                name=opponent,
                showlegend=False,
                hovertemplate=(
                    f"<b>{opponent} Counter</b><br>"
                    f"Minute: {int(c['minute'])}'<br>"
                    f"xG conceded: {c['xg_conceded']:.2f}<br>"
                    f"Shots: {int(c['led_to_shot'])}<br>"
                    "<extra></extra>"
                )
            ))

    # ── Team labels ────────────────────────────────────────
    fig.add_annotation(
        x=2, y=0.15,
        text=f"<b>{team}</b>",
        showarrow=False,
        font=dict(color=color, size=10),
        xanchor='left'
    )
    fig.add_annotation(
        x=2, y=-0.15,
        text=f"<b>{opponent}</b>",
        showarrow=False,
        font=dict(color='tomato', size=10),
        xanchor='left'
    )

    # ── HT line ────────────────────────────────────────────
    fig.add_vline(
        x=45, line_dash='dot',
        line_color='#475569', line_width=1,
        annotation_text='HT',
        annotation_font_color='#475569',
        annotation_font_size=10,
    )

    # ── Zero line ─────────────────────────────────────────
    fig.add_hline(
        y=0, line_color='#2d3f50',
        line_width=1.5
    )

    fig.update_layout(
        paper_bgcolor='#0e1117',
        plot_bgcolor='#151b23',
        font=dict(color='#e2e8f0', family='DM Sans'),
        height=300,
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(
            title='Minute',
            range=[0, 95],
            tickvals=[0, 15, 30, 45, 60, 75, 90],
            gridcolor='#1e2a38',
            zeroline=False,
            color='#64748b',
        ),
        yaxis=dict(
            title='xG',
            gridcolor='#1e2a38',
            zeroline=False,
            color='#64748b',
        ),
        hovermode='closest',
        showlegend=False,
    )

    return fig


def plot_counter_zone_breakdown(df_counters):
    """
    Bar chart showing counter-attack volume and
    efficiency broken down by starting zone.

    High zone = won ball in opponent half (x > 60)
    Mid zone  = won ball in midfield (x 40-60)
    Low zone  = won ball in own half (x < 40)
    """
    import plotly.graph_objects as go
    import pandas as pd

    if df_counters.empty:
        return None

    zone_order  = ['high', 'mid', 'low']
    zone_labels = ['High (opp half)', 'Mid', 'Low (own half)']

    zone_stats = df_counters.groupby('zone').agg(
        total=('led_to_shot', 'count'),
        shots=('led_to_shot', 'sum'),
        goals=('led_to_goal', 'sum'),
        xg=('xg', 'sum'),
    ).reindex(zone_order).fillna(0)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=zone_labels,
        y=zone_stats['total'],
        name='Counters',
        marker_color='#334155',
        opacity=0.9,
    ))
    fig.add_trace(go.Bar(
        x=zone_labels,
        y=zone_stats['shots'],
        name='Led to Shot',
        marker_color='royalblue',
    ))
    fig.add_trace(go.Bar(
        x=zone_labels,
        y=zone_stats['goals'],
        name='Led to Goal',
        marker_color='gold',
    ))

    fig.update_layout(
        paper_bgcolor='#0e1117',
        plot_bgcolor='#151b23',
        font=dict(color='#e2e8f0', family='DM Sans'),
        height=280,
        barmode='overlay',
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(gridcolor='#1e2a38', color='#64748b'),
        yaxis=dict(
            title='Count',
            gridcolor='#1e2a38',
            color='#64748b'
        ),
        legend=dict(
            orientation='h', y=1.05,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=10)
        ),
    )

    return fig
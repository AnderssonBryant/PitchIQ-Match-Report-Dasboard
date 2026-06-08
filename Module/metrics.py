import pandas as pd


def compute_match_stats(passes, shots, pressures, def_actions, selected_team):
    """
    Takes sliced event DataFrames for a single team.
    Returns a dict of computed stats.
    """
    passes       = passes[passes['team_name'] == selected_team]
    shots        = shots[shots['team_name'] == selected_team]
    pressures     = pressures[pressures['team_name'] == selected_team]
    def_actions = def_actions[def_actions['team_name'] == selected_team]

    completed_passes = passes[passes['outcome_name'].isna()]
    pass_pct = (len(completed_passes) / len(passes) * 100) if len(passes) else 0

    prog_passes = passes[
        (passes['end_x'] - passes['x'] > 10) & 
        (passes['end_x'] > 60)
    ] if 'end_x' in passes.columns else pd.DataFrame()

    key_passes = passes[passes['pass_goal_assist'].notna()] \
                 if 'pass_goal_assist' in passes.columns else pd.DataFrame()

    xG = shots['shot_statsbomb_xg'].sum() \
         if 'shot_statsbomb_xg' in shots.columns else 0
    xG = round(float(xG), 2)

    goals = len(shots[shots['outcome_name'] == 'Goal'])
    sot   = len(shots[shots['outcome_name'].isin(['Goal', 'Saved'])])
    big_chances = len(shots[shots['shot_statsbomb_xg'] > 0.3]) \
                  if 'shot_statsbomb_xg' in shots.columns else 0


    tackles      = len(def_actions[def_actions['sub_type_name'] == 'Tackle'])
    interceptions = len(def_actions[def_actions['type_name'] == 'Interception'])
    clearances   = len(def_actions[def_actions['type_name'] == 'Clearance'])
    blocks       = len(def_actions[def_actions['type_name'] == 'Block'])

    return {
        'shots':           len(shots),
        'sot':             sot,
        'goals':           goals,
        'xG':              xG,
        'big_chances':     big_chances,
        'passes':          len(passes),
        'pass_pct':        round(pass_pct, 1),
        'prog_passes':     len(prog_passes),
        'key_passes':      len(key_passes),
        'pressures':       len(pressures),
        'tackles':         tackles,
        'interceptions':   interceptions,
        'clearances':      clearances,
        'blocks':          blocks,
    }


def build_xg_story(shots):
    shots = shots.copy()
    shots["xg"]      = shots["shot_statsbomb_xg"].fillna(0)
    shots["is_goal"] = shots["outcome_name"] == "Goal"

    # ✅ No offset needed — minute is already the real match minute
    result = {}
    for team, grp in shots.groupby("team_name"):
        grp = grp.sort_values("minute")[
            ["minute", "xg", "is_goal"]
        ].copy()

        origin = pd.DataFrame([{"minute": 0, "xg": 0, "is_goal": False}])
        grp    = pd.concat([origin, grp], ignore_index=True)
        grp["cumulative_xg"] = grp["xg"].cumsum()
        result[team] = grp

    return result


# utils/metrics.py

def build_momentum(events, home_team, away_team, window=3):
    """
    Computes match momentum as a rolling event count per team.
    Positive = home team dominant, Negative = away team dominant.
    
    window : rolling minute window (3 = 3-minute rolling average)
    """
    # Events that indicate dominance/activity
    momentum_types = [
        'Pass', 'Carry', 'Pressure', 'Dribble',
        'Shot', 'Ball Recovery', 'Interception'
    ]

    ev = events[events['type_name'].isin(momentum_types)].copy()
    ev = ev[ev['period'].isin([1, 2])]  # regular time only

    # Count events per team per minute
    home_ev = ev[ev['team_name'] == home_team].groupby('minute').size()
    away_ev = ev[ev['team_name'] == away_team].groupby('minute').size()

    # Align to full 90-minute index
    all_minutes = pd.RangeIndex(0, 91)
    home_ev = home_ev.reindex(all_minutes, fill_value=0)
    away_ev = away_ev.reindex(all_minutes, fill_value=0)

    # Rolling average to smooth it out
    home_rolling = home_ev.rolling(window=window, center=True,
                                   min_periods=1).mean()
    away_rolling = away_ev.rolling(window=window, center=True,
                                   min_periods=1).mean()

    # Momentum = home - away
    # Positive = home dominant, Negative = away dominant
    momentum = home_rolling - away_rolling

    return pd.DataFrame({
        'minute':   all_minutes,
        'momentum': momentum.values,
        'home':     home_rolling.values,
        'away':     away_rolling.values,
    })

def compute_ppda(passes_df,pressures_df,def_actions,team_name):

    opp_passes = passes_df[(passes_df["team_name"] != team_name) & (passes_df["x"] < 72)]

    team_def_actions = def_actions[ (def_actions["x"] > 48)]

    team_pressures = pressures_df[(pressures_df["x"] > 48)]

    if len(team_def_actions) == 0:
        return None

    return round(
        len(opp_passes) /
        (len(team_def_actions) + len(team_pressures)),
        2
    )


def build_transition_metrics(events, team):
    import pandas as pd

    opponent = [
        t for t in events['team_name'].unique()
        if t != team
    ][0]

    # ─────────────────────────────────────────────────────
    # ATTACKING — team's counter possessions
    # ─────────────────────────────────────────────────────

    # Get possession IDs where THIS TEAM had From Counter
    team_counter_poss = events[
        (events['play_pattern_name'] == 'From Counter') &
        (events['team_name'] == team)
    ]['possession'].unique()

    possession_summary = []

    for poss_id in team_counter_poss:
        # All events in possession — but filter to team only
        poss_all = events[
            events['possession'] == poss_id
        ].sort_values('index')

        # ✅ Only this team's events for metrics
        poss_team = poss_all[
            poss_all['team_name'] == team
        ].copy()

        if poss_team.empty:
            continue

        first     = poss_team.iloc[0]
        start_x   = float(first.get('x', 0) or 0)
        start_y   = float(first.get('y', 40) or 40)
        start_min = int(first['minute'])

        shots   = poss_team[poss_team['type_name'] == 'Shot']
        carries = poss_team[poss_team['type_name'] == 'Carry']
        passes  = poss_team[poss_team['type_name'] == 'Pass']
        max_x   = float(poss_team['x'].max()) \
                  if 'x' in poss_team.columns else start_x

        try:
            t0 = pd.to_datetime(poss_team['timestamp'].iloc[0])
            t1 = pd.to_datetime(poss_team['timestamp'].iloc[-1])
            duration = (t1 - t0).seconds
        except Exception:
            duration = None

        xg = float(shots['shot_statsbomb_xg'].sum()) \
             if len(shots) and \
             'shot_statsbomb_xg' in shots.columns else 0

        possession_summary.append({
            'possession_id':   poss_id,
            'minute':          start_min,
            'start_x':         start_x,
            'start_y':         start_y,
            'max_x':           max_x,
            'distance_gained': max_x - start_x,
            'n_events':        len(poss_team),
            'n_passes':        len(passes),
            'n_carries':       len(carries),
            'n_shots':         len(shots),
            'led_to_shot':     len(shots) > 0,
            'led_to_goal':     len(shots[
                shots['outcome_name'] == 'Goal'
            ]) > 0 if len(shots) else False,
            'xg':              xg,
            'duration_sec':    duration,
            'zone':            'high'  if start_x > 60
                               else 'mid' if start_x > 40
                               else 'low',
            'trigger':         first.get('type_name', 'Unknown'),
        })

    df_counters = pd.DataFrame(
        possession_summary
    ) if possession_summary else pd.DataFrame()

    # ─────────────────────────────────────────────────────
    # DEFENDING — opponent's counter possessions
    # ✅ Only get possessions where OPPONENT had From Counter
    # NOT the same list as above
    # ─────────────────────────────────────────────────────

    opp_counter_poss = events[
        (events['play_pattern_name'] == 'From Counter') &
        (events['team_name'] == opponent)   # ← opponent, not team
    ]['possession'].unique()

    # ✅ Exclude any possession that was ALSO a team counter
    # (edge case — same possession can't be both)
    opp_counter_poss = [
        p for p in opp_counter_poss
        if p not in team_counter_poss
    ]

    opp_summary = []

    for poss_id in opp_counter_poss:
        poss_all = events[
            events['possession'] == poss_id
        ].sort_values('index')

        # ✅ Only opponent's events for metrics
        poss_opp = poss_all[
            poss_all['team_name'] == opponent
        ].copy()

        if poss_opp.empty:
            continue

        first   = poss_opp.iloc[0]
        shots   = poss_opp[poss_opp['type_name'] == 'Shot']

        start_x = float(first.get('x', 0) or 0)
        start_y = float(first.get('y', 40) or 40)

        xg = float(shots['shot_statsbomb_xg'].sum()) \
             if len(shots) and \
             'shot_statsbomb_xg' in shots.columns else 0

        try:
            t0 = pd.to_datetime(poss_opp['timestamp'].iloc[0])
            t1 = pd.to_datetime(poss_opp['timestamp'].iloc[-1])
            duration = (t1 - t0).seconds
        except Exception:
            duration = None

        opp_summary.append({
            'possession_id': poss_id,
            'minute':        int(first['minute']),
            'start_x':       start_x,
            'start_y':       start_y,
            'n_shots':       len(shots),
            'led_to_shot':   len(shots) > 0,
            'led_to_goal':   len(shots[
                shots['outcome_name'] == 'Goal'
            ]) > 0 if len(shots) else False,
            'xg_conceded':   xg,
            'duration_sec':  duration,
        })

    df_opp_counters = pd.DataFrame(
        opp_summary
    ) if opp_summary else pd.DataFrame()

    # ─────────────────────────────────────────────────────
    # SUMMARY METRICS
    # ─────────────────────────────────────────────────────
    total     = len(df_counters)
    to_shot   = int(df_counters['led_to_shot'].sum()) \
                if total else 0
    to_goal   = int(df_counters['led_to_goal'].sum()) \
                if total else 0

    total_opp   = len(df_opp_counters)
    opp_to_shot = int(df_opp_counters['led_to_shot'].sum()) \
                  if total_opp else 0
    opp_to_goal = int(df_opp_counters['led_to_goal'].sum()) \
                  if total_opp else 0

    return {
        # Attacking
        'counters_initiated':   total,
        'counters_to_shot':     to_shot,
        'counters_to_goal':     to_goal,
        'counter_efficiency':   round(
            to_shot / total * 100, 1
        ) if total else 0,
        'counter_conversion':   round(
            to_goal / total * 100, 1
        ) if total else 0,
        'avg_distance':         round(
            float(df_counters['distance_gained'].mean()), 1
        ) if total else 0,
        'avg_duration':         round(
            float(
                df_counters['duration_sec'].dropna().mean()
            ), 1
        ) if total else 0,
        'counter_xg':           round(
            float(df_counters['xg'].sum()), 2
        ) if total else 0,

        # Defending
        'opp_counters':          total_opp,
        'opp_counters_to_shot':  opp_to_shot,
        'opp_counters_to_goal':  opp_to_goal,
        'opp_vulnerability':     round(
            opp_to_shot / total_opp * 100, 1
        ) if total_opp else 0,
        'xg_conceded_counter':   round(
            float(df_opp_counters['xg_conceded'].sum()), 2
        ) if total_opp else 0,
        'avg_opp_duration':     round(
            float(
                df_opp_counters['duration_sec'].dropna().mean()
            ), 1
        ) if total_opp else 0,

        # DataFrames
        'df_counters':     df_counters,
        'df_opp_counters': df_opp_counters,
    }

def inspect_counter_possessions(events, team):
    """
    Prints a summary of each counter-attack possession.
    Useful for debugging and understanding the data.
    """
    counters = events[
        (events['play_pattern_name'] == 'From Counter') &
        (events['team_name'] == team)
    ]

    for poss_id in counters['possession'].unique():
        poss = events[
            events['possession'] == poss_id
        ].sort_values('index')

        print(f"\n── Possession {poss_id} "
              f"(min {poss['minute'].iloc[0]}) ──")
        print(poss[['minute', 'type_name',
                    'player_name', 'outcome_name',
                    'x', 'y']].to_string())
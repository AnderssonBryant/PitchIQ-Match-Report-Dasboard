# utils/data_loader.py
import streamlit as st
from statsbombpy import sb
from mplsoccer import Sbopen

parser = Sbopen()

@st.cache_data(ttl=3600)
def get_competitions():
    return parser.competition()

@st.cache_data(ttl=1800)
def get_matches(competition_id, season_id):
    return parser.match(competition_id=competition_id, season_id=season_id)

@st.cache_data
def get_lineups(match_id):
    return parser.lineup(match_id=match_id)

@st.cache_data
def get_raw_events(match_id):
    """Unsplit — still useful for overview metrics like possession, timeline."""
    df_events,df_related,df_freeze,df_tactics = parser.event(match_id=match_id)
    return df_events,df_related,df_freeze,df_tactics

@st.cache_data
def get_events_only(match_id):
    """Just the main events DataFrame (convenience wrapper)."""
    df_event, _, _, _ = get_raw_events(match_id)
    return df_event


# ── Accessors — thin wrappers over get_split_events ───────

def get_passes(match_id, team=None):
    df_event = get_events_only(match_id)
    passes = df_event[df_event['type_name'] == 'Pass']
    return passes if team is None else passes[passes['team_name'] == team]

def get_shots(match_id, team=None):
    df_event = get_events_only(match_id)
    shots = df_event[df_event['type_name'] == 'Shot']
    return shots if team is None else shots[shots['team_name'] == team]

def get_carries(match_id, team=None):
    df_event = get_events_only(match_id)
    carries = df_event[df_event['type_name'] == 'Carry']
    return carries if team is None else carries[carries['team_name'] == team]

def get_pressures(match_id, team=None):
    df_event = get_events_only(match_id)
    pressures = df_event[df_event['type_name'] == 'Pressure']
    return pressures if team is None else pressures[pressures['team_name'] == team]

def get_dribbles(match_id, team=None):
    df_event = get_events_only(match_id)
    dribbles = df_event[df_event['type_name'] == 'Dribble']
    return dribbles if team is None else dribbles[dribbles['team_name'] == team]

def get_defensive_actions(match_id, team=None):
    df_event = get_events_only(match_id)
    def_actions = df_event[(df_event['type_name']=='Interception') | (df_event['type_name']=='Clearance') | (df_event['type_name']=='Block') | (df_event['type_name']=='Ball Recovery') | (df_event['type_name']=='Duel')]
    return def_actions if team is None else def_actions[def_actions['team_name'] == team]

def get_turnovers(match_id, team=None):
    df_event = get_events_only(match_id)
    turnovers = df_event[(df_event['type_name']=='Dispossession') | (df_event['type_name']=='Misconduct')]
    return turnovers if team is None else turnovers[turnovers['team_name'] == team]

@st.cache_data
def get_starting_xi(match_id):
    df_event, _, _, df_tactics = parser.event(match_id)
    df_lineup = parser.lineup(match_id)

    # ── Get Starting XI event IDs + formation ─────────────
    xi_events = df_event[df_event['type_name'] == 'Starting XI'][['id', 'team_name', 'tactics_formation']]

    # ── Filter tactics to Starting XI events only ─────────
    # event_tactics_id == id of the Starting XI event
    xi_ids = xi_events['id'].tolist()
    df_tactics_xi = df_tactics[
        df_tactics['id'].isin(xi_ids)
    ].copy()

    # ── Merge lineup for team info + nickname ─────────────
    df_starting = df_tactics_xi.merge(
        df_lineup[['player_id', 'player_nickname',
                   'team_id', 'team_name', 'country_name']],
        on='player_id',
        how='left'
    )

    # ── Build result dict ──────────────────────────────────
    result = {}

    for team in df_starting['team_name'].unique():
        team_df  = df_starting[df_starting['team_name'] == team].copy()

        # Get formation for this team
        formation = xi_events[
            xi_events['team_name'] == team
        ]['tactics_formation'].values[0]

        lineup = []
        for _, row in team_df.iterrows():
            lineup.append({
                'player_id':       row['player_id'],
                'player':          row['player_name'],
                'player_nickname': row.get('player_nickname', ''),
                'jersey_number':   row['jersey_number'],
                'position_id':     row['position_id'],
                'position_name':   row['position_name'],
                'country_name':    row.get('country_name', ''),
            })

        result[team] = {
            'formation': formation,
            'lineup':    lineup,
        }

    return result


@st.cache_data
def get_substitutions(match_id):
    """
    Returns all substitution events for a match.

    Columns you'll get from Sbopen:
    - minute          → when the sub happened
    - team_name       → which team made the sub
    - player_name     → player going OFF
    - substitution_replacement → player coming ON
    - period          → which period (1 or 2)
    """
    df = get_events_only(match_id)
    subs = df[df['type_name'] == 'Substitution'].copy()
    return subs
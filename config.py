# config.py

# ── Streamlit dark theme CSS ──────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0e1117 !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #151b23 !important;
    border-right: 1px solid #1e2a38 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}
[data-baseweb="select"] > div {
    background-color: #1e2a38 !important;
    border-color: #2d3f50 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] > div:hover {
    border-color: #3b82f6 !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #151b23 !important;
    border-bottom: 1px solid #1e2a38 !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #64748b !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: color 0.2s ease !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #3b82f6 !important;
    background-color: #1e2a38 !important;
    border-bottom: 2px solid #3b82f6 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #151b23 !important;
    border: 1px solid #1e2a38 !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label {
    color: #64748b !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-size: 22px !important;
    font-weight: 600 !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border: 1px solid #1e2a38 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    text-align: center !important;
}

/* Divider */
hr {
    border-color: #1e2a38 !important;
}

/* Headings */
h1, h2, h3 {
    color: #f1f5f9 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Caption / small text */
[data-testid="stCaptionContainer"] {
    color: ##64748b !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #94a3b8 !important;
}
</style>
"""

# ── Matplotlib global style ───────────────────────────────
import matplotlib as mpl
mpl.rcParams.update({
    "figure.facecolor":  "#0e1117",
    "axes.facecolor":    "#0e1117",
    "text.color":        "#e2e8f0",
    "axes.labelcolor":   "#94a3b8",
    "xtick.color":       "#475569",
    "ytick.color":       "#475569",
    "axes.edgecolor":    "#1e2a38",
    "grid.color":        "#1e2a38",
    "font.family":       "DejaVu Sans",
})

# ── Color tokens ─────────────────────────────────────────
BG_PRIMARY     = "#0e1117"
BG_SECONDARY   = "#151b23"
BG_CARD        = "#1e2a38"
BORDER         = "#2d3f50"
TEXT_PRIMARY   = "#e2e8f0"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED     = "#475569"
ACCENT_BLUE    = "#3b82f6"
ACCENT_AMBER   = "#f59e0b"   # GK highlight
HOME_COLOR     = "#3b82f6"   # blue
AWAY_COLOR     = "#f97316"   # orange

# ── Pitch colors ──────────────────────────────────────────
PITCH_COLOR    = "#0d1f12"   # very dark green — readable, not distracting
LINE_COLOR     = "#1e4028"   # subtle dark green lines


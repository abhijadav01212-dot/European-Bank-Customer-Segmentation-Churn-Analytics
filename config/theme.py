"""Central theme & color constants for the banking analytics app.

Enterprise banking theme: white background, royal blue accents, black text.
No gradients, no glassmorphism, no icons/emoji anywhere in the UI.
"""

PRIMARY = "#2563EB"       # Royal Blue
SECONDARY = "#FFFFFF"     # White
TEXT = "#111827"          # Black (near-black)
BORDER = "#E5E7EB"
HOVER = "#DBEAFE"
ROW_ALT = "#F9FAFB"
BG = "#FFFFFF"
CARD_BG = "#FFFFFF"

# Monochrome-blue sequence for multi-series charts
CHART_SEQUENCE = ["#2563EB", "#60A5FA", "#1E40AF", "#93C5FD", "#1D4ED8", "#BFDBFE"]

STATUS_COLORS = {"Retained": "#2563EB", "Churned": "#93C5FD"}
GEO_COLORS = {"France": "#2563EB", "Germany": "#1E40AF", "Spain": "#93C5FD"}
GENDER_COLORS = {"Male": "#2563EB", "Female": "#93C5FD"}

PLOTLY_TEMPLATE = "plotly_white"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', 'Poppins', sans-serif !important;
}}

.stApp {{
    background: {BG};
    color: {TEXT};
}}

/* ---- Page titles ---- */
h1 {{
    color: {PRIMARY} !important;
    font-weight: 700 !important;
    font-size: 32px !important;
    letter-spacing: -0.01em;
}}
h2, h3 {{
    color: {PRIMARY} !important;
    font-weight: 700 !important;
}}
p, span, label, div {{
    color: {TEXT};
}}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
    background: {SECONDARY};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}
section[data-testid="stSidebar"] label {{
    font-weight: 600;
}}
/* selected page in the page-nav list */
section[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background-color: {PRIMARY} !important;
    border-radius: 8px;
}}
section[data-testid="stSidebarNav"] a[aria-current="page"] span {{
    color: {SECONDARY} !important;
}}
section[data-testid="stSidebarNav"] a {{
    border-radius: 8px;
}}
section[data-testid="stSidebarNav"] a:hover {{
    background-color: {HOVER} !important;
}}

/* ---- KPI Cards: blue header, white header text, black value ---- */
.kpi-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(17,24,39,0.06);
    transition: box-shadow 0.15s ease;
}}
.kpi-card:hover {{
    box-shadow: 0 4px 12px rgba(37,99,235,0.15);
}}
.kpi-label {{
    background: {PRIMARY};
    color: {SECONDARY};
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    padding: 9px 16px;
}}
.kpi-value {{
    font-size: 1.65rem;
    font-weight: 800;
    color: {TEXT};
    padding: 14px 16px 16px 16px;
}}

/* ---- Buttons ---- */
.stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {{
    background: {PRIMARY};
    color: {SECONDARY};
    border-radius: 8px;
    border: 1px solid {PRIMARY};
    font-weight: 600;
}}
.stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover {{
    background: #1D4ED8;
    border-color: #1D4ED8;
    color: {SECONDARY};
}}

/* ---- Dropdowns / multiselect / selectbox ---- */
div[data-baseweb="select"] > div {{
    background-color: {SECONDARY} !important;
    border: 1px solid {PRIMARY} !important;
    border-radius: 8px !important;
}}
span[data-baseweb="tag"], div[data-baseweb="tag"] {{
    background-color: {HOVER} !important;
    background: {HOVER} !important;
    border: 1px solid {PRIMARY} !important;
    color: {TEXT} !important;
}}
span[data-baseweb="tag"] *, div[data-baseweb="tag"] * {{
    color: {TEXT} !important;
    fill: {TEXT} !important;
}}
div[data-baseweb="select"] svg {{
    fill: {PRIMARY} !important;
}}
ul[data-baseweb="menu"] {{
    background-color: {SECONDARY} !important;
    border: 1px solid {BORDER} !important;
}}
li[data-baseweb="menu-item"] {{
    color: {TEXT} !important;
    background-color: {SECONDARY} !important;
}}
li[data-baseweb="menu-item"]:hover {{
    background-color: {HOVER} !important;
}}

/* ---- Radio buttons ---- */
div[data-testid="stRadio"] label {{
    color: {TEXT} !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] label div:first-child {{
    border-color: {PRIMARY} !important;
}}

/* ---- Sliders ---- */
div[data-testid="stSlider"] [data-baseweb="slider"] div {{
    background-color: {PRIMARY} !important;
}}
div[data-testid="stSlider"] [role="slider"] {{
    background-color: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}

/* ---- Tables / dataframes ---- */
.stDataFrame {{
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
[data-testid="stDataFrame"] thead tr th {{
    background-color: {PRIMARY} !important;
    color: {SECONDARY} !important;
    font-weight: 600 !important;
}}
[data-testid="stDataFrame"] tbody tr:nth-child(even) {{
    background-color: {ROW_ALT} !important;
}}

/* ---- Alerts / recommendations ---- */
div[data-testid="stAlert"] {{
    background: {SECONDARY};
    border: 1px solid {BORDER};
    border-left: 4px solid {PRIMARY};
    color: {TEXT};
    border-radius: 8px;
}}

hr {{ border-color: {BORDER}; }}
[data-testid="stMetricValue"] {{ color: {TEXT}; }}

/* ---- Filter panel header ---- */
.filter-panel-header {{
    background: {PRIMARY};
    color: {SECONDARY} !important;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 8px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
}}
.filter-panel-header * {{
    color: {SECONDARY} !important;
}}

/* ---- Forms ---- */
div[data-testid="stForm"] {{
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1rem;
}}
</style>
"""

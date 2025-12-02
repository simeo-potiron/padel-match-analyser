# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages


# Streamlit Package
import streamlit as st


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define GLOBAL VARIABLES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# ~~~~~~~~    Streamlit    ~~~~~~~~ #
# Global App Settings
BASE_URL = st.secrets["app"]["base_url"]
# Airtable
AT_TOKEN = st.secrets["airtable"]["token"]
# Google Cloud
GCP_SERVICE_ACCOUNT = st.secrets["google-service-account"]
# SMTP
SMTP_SERVER = st.secrets["email"]["smtp_server"]
SMTP_PORT = st.secrets["email"]["smtp_port"]
SMTP_SENDER_EMAIL = st.secrets["email"]["sender_email"]
SMTP_APP_PASSWORD = st.secrets["email"]["app_password"]
# Security
PASSWORD_PEPPER = st.secrets["password"]["pepper"]
# Display
DEFAULT_DISPLAYED_MATCHES = 3
SESSION_STATE_MATCH_FIELDS = ["match_admin", "match_viewers", "match_board", "match_updated"]

# ~~~~~~~~    Google Cloud    ~~~~~~~~ #
GCS_BUCKET = "padel-matchs"

# ~~~~~~~~    Airtable    ~~~~~~~~ #
# Store Airtable Ids
PADEL_BASE_ID = "appHpJoih6uBVyjyC"
# Users table
USERS_TABLE_ID = "tblHyMeKRpnvgx6mb"
USER_SESSION_STATE_FIELDS = [
    "email"
]
# Matches table
MATCHES_TABLE_ID = "tblxB67Tdd0S2Yl5s"
MATCH_SESSION_STATE_FIELDS = [
    "match_id",
    "name", 
    "date", 
    "display_score",
    "video",
    "editor",
    "viewers_footprint"
]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define TEMPLATES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# ~~~~~~~~    Score Board    ~~~~~~~~ #
TEMPLATE_SCORE_BOARD = {
    "format": "",
    "teams": {
        "A": {},
        "B": {}
    },
    "serving": {
        "previous": None,
        "current": None,
        "next": None
    },
    "match": {
        "score": [],
        "score_tb": [],
        "sets": {
            "A": 0,
            "B": 0
        },
        "games": {
            "A": 0,
            "B": 0
        },
        "points": {
            "A": 0,
            "B": 0
        },
    },
    "live_stats": {
        "serving": [],
        "points_won": [],
        "match_points": [],
        "break_points": [],
        "breaks": [],
        "events": [],
        "A1": [],
        "A2": [],
        "B1": [],
        "B2": []
    },
    "winner": None
}

# ~~~~~~~~    Formats    ~~~~~~~~ #
TEMPLATE_FORMATS = {
    "A1": {
        "description": "2 sets de 6 jeux, avec avantages.",
        "sets": 2,
        "games": 6,
        "advantages": True, 
        "super_tb": False,
        "tie_break": 0
    },
    "A2": {
        "description": "2 sets de 6 jeux, sans avantages.",
        "sets": 2,
        "games": 6,
        "advantages": False, 
        "super_tb": False,
        "tie_break": 0
    },
    "B1": {
        "description": "2 sets de 6 jeux, avec avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 6,
        "advantages": True, 
        "super_tb": True,
        "tie_break": 0
    },
    "B2": {
        "description": "2 sets de 6 jeux, sans avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 6,
        "advantages": False, 
        "super_tb": True,
        "tie_break": 0
    },
    "C1": {
        "description": "2 sets de 4 jeux, avec avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 4,
        "advantages": True, 
        "super_tb": True,
        "tie_break": 0
    },
    "C2": {
        "description": "2 sets de 4 jeux, sans avantages. Super TB au 3ème.",
        "sets": 2,
        "games": 4,
        "advantages": False, 
        "super_tb": True,
        "tie_break": 0
    },
    "D1": {
        "description": "1 set de 9 jeux, avec avantages. TB à 8/8.",
        "sets": 1,
        "games": 9,
        "advantages": True, 
        "super_tb": False,
        "tie_break": -1
    },
    "D2": {
        "description": "1 set de 9 jeux, sans avantages. TB à 8/8.",
        "sets": 1,
        "games": 9,
        "advantages": False, 
        "super_tb": False,
        "tie_break": -1
    },
    "E": {
        "description": "Super TB en 10 points.",
        "sets": 1,
        "games": 0,
        "advantages": False,
        "super_tb": True,
        "tie_break": 0
    }
}
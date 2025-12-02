# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
import copy
import json

# Datetime Packages
from datetime import datetime

# Streamlit Package
import streamlit as st

# Airtable Package
from pyairtable import Api


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import UTILS FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from .utils import union_lists


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import GLOBAL VARIABLES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from storage import *


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Authenticate Airtable API    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

AT_API = Api(AT_TOKEN)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def get_session_matches():
    """
    Update session_state matches
    """
    # Connexion à Airtable
    matches_table = AT_API.table(PADEL_BASE_ID, MATCHES_TABLE_ID)
    
    # Récupère les matchs
    formula = f"""FIND('""token"":""{st.session_state.token}""', viewers) > 0"""
    all_matches = matches_table.all(formula=formula)

    session_matches = [{key: val for key, val in match.get("fields").items() if key in MATCH_SESSION_STATE_FIELDS} for match in all_matches]
    if session_matches:
        session_matches.sort(reverse=True, key=lambda x: x.get("date", "") + x.get("name", ""))

    # Mettre à jour la session
    st.session_state.matches = session_matches

def upsert_match(type, match_id=None, match_hash=None):
    """
    Upsert a match in airtable:
        - Store a new match
        - Update stored match with latest changes
        - Delete a match
    """
    # Connexion à Airtable
    matches_table = AT_API.table(PADEL_BASE_ID, MATCHES_TABLE_ID)

    if type == "create" and match_hash:
        # Créer le record
        resp = matches_table.create(match_hash)
        
        # Mettre à jour la session
        st.session_state.match_id = resp.get("id")
        st.session_state.match_name = None
        st.session_state.match_date = None
        st.session_state.match_admin = True
        st.session_state.match_viewers = json.loads(resp.get("fields").get("viewers_footprint")) 
        st.session_state.match_board = copy.deepcopy(TEMPLATE_SCORE_BOARD)
        st.session_state.match_video = None
        st.session_state.match_updated = False

        # Changer de page pour configurer le nouveau match
        st.switch_page("pages/NewMatch.py")

    elif type == "update" and match_id and match_hash:
        # Mettre à jour le record
        matches_table.update(match_id, match_hash)

    elif type == "delete" and match_id:
        # Mettre à jour le record
        matches_table.delete(match_id)

def open_match(match_id):
    """
    Focus the session on a specific match
    """
    # Connexion à Airtable
    matches_table = AT_API.table(PADEL_BASE_ID, MATCHES_TABLE_ID)

    # Retrieve match data
    match = matches_table.get(match_id)

    # Mettre à jour la session
    st.session_state.match_id = match.get("id")
    st.session_state.match_name = match.get("fields").get("name")
    st.session_state.match_date = match.get("fields").get("date")
    st.session_state.match_admin = st.session_state.token in match.get("fields").get("editor")
    st.session_state.match_viewers = json.loads(match.get("fields").get("viewers_footprint")) 
    st.session_state.match_board = json.loads(match.get("fields").get("board"))
    st.session_state.match_video = match.get("fields").get("video")
    st.session_state.match_updated = False

    # Changer de page
    st.switch_page("pages/Match.py")

def close_current_match():    
    """
    Reset session's followed match
    """
    # Mettre à jour la session
    st.session_state.match_id = None
    st.session_state.match_name = None
    st.session_state.match_date = None
    st.session_state.match_admin = None
    st.session_state.match_viewers = None
    st.session_state.match_board = None
    st.session_state.match_video = None
    st.session_state.match_updated = None

    # Revenir à la Home page
    st.switch_page("Home.py")
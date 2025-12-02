# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
import json
import copy
import time

# Streamlit Package
import streamlit as st


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import UTILS FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from utils import *


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import GLOBAL VARIABLES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from storage import *


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define PAGE    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# ~~~~    Page config    ~~~~ #
st.set_page_config(page_title="Nouveau match", page_icon="➕", layout="wide")


# ~~~~    Initial checks    ~~~~ #
require_login()
if "match_id" not in st.session_state or st.session_state.match_id is None:
    st.switch_page("Home.py")
elif any([el not in st.session_state or st.session_state[el] is None for el in SESSION_STATE_MATCH_FIELDS]):
    st.switch_page("Home.py")


# ~~~~    Global HTML settings    ~~~~ #
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ~~~~    Page core    ~~~~ #
# Header
st.title("🆕 Suivre un nouveau match")

# Select one of available match formats
format_choices = ["--"] + [f"{str(key)}: {val.get('description')}" for key, val in TEMPLATE_FORMATS.items()]
input_format = st.selectbox("Format du match*", format_choices)
match_format = input_format.split(":")[0] if (":" in input_format) else None

# Match options
title_col, toggle_col = st.columns([3, 1])
with title_col:
    st.markdown("### 🎾 Equipes et joueurs")
with toggle_col:
    follow_players_stats = st.toggle("Suivre les stats des joueurs", True)

# Name teams and players
col1, col2 = st.columns(2)
# === Équipe A ===
with col1:
    st.subheader("Équipe A")
    team_a = st.text_input("Nom de l'équipe", key="team1_name")
    player_1a = st.text_input("Joueur 1*", key="team1_p1")
    player_2a = st.text_input("Joueur 2*", key="team1_p2")
# === Équipe B ===
with col2:
    st.subheader("Équipe B")
    team_b = st.text_input("Nom de l'équipe 2", key="team2_name")
    player_1b = st.text_input("Joueur 1*", key="team2_p1")
    player_2b = st.text_input("Joueur 2*", key="team2_p2")

# Launch match
if st.button("✅ Démarrer le match"):
    players = [player_1a, player_2a, player_1b, player_2b]
    if match_format and all(players) and (len(set(players))==len(players)):
        # Update the template board with match teams and format
        st.session_state.match_board.update({
            "format": match_format,
            "max_sets": TEMPLATE_FORMATS[match_format]["sets"]*2-1,
            "follow_players_stats": follow_players_stats,
            "teams": {
                "A": {
                    "name": team_a if team_a else f"{player_1a} / {player_2a}",
                    "player_1": player_1a,
                    "player_2": player_2a
                },
                "B": {
                    "name": team_b if team_b else f"{player_1b} / {player_2b}",
                    "player_1": player_1b,
                    "player_2": player_2b
                }
            }
        })
        # Store updated board in AT
        upsert_match("update", match_id=st.session_state.match_id, match_hash={"board": json.dumps(st.session_state.match_board)})
        st.success("Match créé ! 🚀")
        time.sleep(2)
        st.switch_page("pages/Match.py")
    elif not match_format:
        st.error("Merci de choisir le format sous lequel est joué le match.")
    elif not all(players):
        st.error("Merci de renseigner le nom de tous les joueurs.")
    else:
        st.error("Tous les joueurs doivent être nommés de manière unique.")

import streamlit as st
import json
from utils import require_login, upsert_match
from templates import score_board, formats
import copy

st.set_page_config(page_title="Nouveau match", page_icon="➕", layout="wide")
require_login()

# ✅ Style mobile
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🆕 Suivre un nouveau match")

try:
    # Vérifie que le match est bien stocké en base
    if st.session_state.match_id is None:
        raise Exception
except:
    st.switch_page("Home.py")

# ✅ Liste des formats possibles
format_choices = ["--"] + [f"{str(key)}: {val.get('description')}" for key, val in formats.items()]

# ✅ Choix du format du match
input_format = st.selectbox("Format du match*", format_choices)
match_format = input_format.split(":")[0] if (":" in input_format) else None

title_col, toggle_col = st.columns([3, 1])
with title_col:
    st.markdown("### 🎾 Equipes et joueurs")
with toggle_col:
    follow_players_stats = st.toggle("Suivre les stats des joueurs", True)

# ✅ Deux colonnes (moitié / moitié)
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

# ✅ Validation du formulaire
if st.button("✅ Démarrer le match"):
    players = [player_1a, player_2a, player_1b, player_2b]
    if match_format and all(players) and (len(set(players))==len(players)):
        # Prepare the template
        board = copy.deepcopy(score_board)
        board["format"] = match_format
        board.update({
            "max_sets": formats[match_format]["sets"]*2-1,
            "follow_players_stats": follow_players_stats
        })
        board["teams"]["A"] = {
            "name": team_a if team_a else f"{player_1a} / {player_2a}",
            "player_1": player_1a,
            "player_2": player_2a
        }
        board["teams"]["B"] = {
            "name": team_b if team_b else f"{player_1b} / {player_2b}",
            "player_1": player_1b,
            "player_2": player_2b
        }
        # Store score board in session_state
        st.session_state.board = board
        print(st.session_state.match_id)
        upsert_match("update", match_id=st.session_state.match_id, match_hash={"board": json.dumps(st.session_state.board)})

        # ➜ futur : envoi au backend + passage au scoring
        st.success("Match créé ! 🚀")
        st.switch_page("pages/Match.py")
    elif not match_format:
        st.error("Merci de choisir le format sous lequel est joué le match.")
    elif not all(players):
        st.error("Merci de renseigner le nom de tous les joueurs.")
    else:
        st.error("Tous les joueurs doivent être nommés de manière unique.")

import streamlit as st
from utils import require_login
from update_score import point_won

st.set_page_config(page_title="Live Match", page_icon="🔴", layout="wide")
require_login()

# ✅ Style mobile
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stColumn > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    table {
        text-align: center !important;
        font-size: 1.4rem !important;
        width: 100%;
        border-collapse: collapse;
        background-color: #0A4DA3;
        color: white;
        border-radius: 10px;
        overflow: hidden;
    }
    th, td {
        padding: 8px;
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    th {
        background-color: rgba(255,255,255,0.15); /* léger contraste */
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔴 Match en direct")

try:
    # Vérifie que board ait bien été initialisé et que le match est bien stocké en base
    if st.session_state.board is None or st.session_state.match_id is None:
        raise Exception
except:
    st.switch_page("Home.py")


@st.dialog("Serveur", width="small", dismissible=False, on_dismiss="rerun")
def choose_server():
    # Check what choices are available
    if st.session_state.board["serving"]["previous"] is None:
        available_teams = ["A", "B"]
    else:
        available_teams = ["A" if st.session_state.board["serving"]["previous"][0] == "B" else "B"]
    # Organise choices
    st.write("Qui va servir ?")
    col_p1, col_p2 = st.columns(2)
    for team in available_teams:
        with col_p1:
            if st.button(st.session_state.board["teams"][team]["player_1"]):
                st.session_state.board["serving"]["current"] = f"{team}1"
                st.rerun()
        with col_p2:
            if st.button(st.session_state.board["teams"][team]["player_2"]):
                st.session_state.board["serving"]["current"] = f"{team}2"
                st.rerun()

# Check if the current serving player is set
if st.session_state.board["serving"]["current"] is None:
    choose_server()

# Vérifie si le match est fini
if st.session_state.board["winner"] is not None:
    # Initiate recap_display
    st.session_state.recap_display = {
        "match": 0,
        "players": 0,
        "video": 0
    }
    st.switch_page("pages/Recap.py")

@st.dialog("Arrêter de suivre les stats des joueurs ?", width="small", dismissible=False)
def stop_stats():
    # st.markdown("### Souhaitez vous vraiment couper le suivi des statistiques joueurs ?")
    yes_col, no_col = st.columns(2)
    with yes_col:
        if st.button("Oui"):
            st.session_state.board["follow_players_stats"] = False
            st.rerun()
    with no_col:
        if st.button("Non"):
            st.rerun()

# ✅ Affichage tableau du score
col1, col2, col3, col4 = st.columns([2,2,2,2])
with col1: 
    st.subheader("Score du match")
with col3:
    if st.session_state.board["follow_players_stats"]:
        if st.button("🛑 Stopper stats joueurs", type="tertiary", key="stop_stats"):
            stop_stats()
with col4:
    if st.button("⏸️ Interrompre le match", type="tertiary", key="stop_match", ):
        st.session_state.board["winner"] = "-"
        st.rerun()

max_sets = st.session_state.board["max_sets"]
score_table_html = f"""
<table>
    <tr>
        <th></th>
        {"".join([f"<th>Set {k+1}</th>" for k in range(max_sets)])}
        <th>Game</th>
    </tr>
    <tr>
        <td><b>{f"{st.session_state.board['teams']['A']['player_1']}{'🟡' if st.session_state.board['serving']['current'] == 'A1' else ''}<br>{st.session_state.board['teams']['A']['player_2']}{'🟡' if st.session_state.board['serving']['current'] == 'A2' else ''}"}</b></td>
        {f"<td>{st.session_state.board['match']['score'][0]['A'] if len(st.session_state.board['match']['score'])>=1 else (st.session_state.board['match']['games']['A'] if len(st.session_state.board['match']['score']) >= 0 else '')}</td>" if max_sets >= 1 else ""}
        {f"<td>{st.session_state.board['match']['score'][1]['A'] if len(st.session_state.board['match']['score'])>=2 else (st.session_state.board['match']['games']['A'] if len(st.session_state.board['match']['score']) >= 1 else '')}</td>" if max_sets >= 2 else ""}
        {f"<td>{st.session_state.board['match']['score'][2]['A'] if len(st.session_state.board['match']['score'])>=3 else (st.session_state.board['match']['games']['A'] if len(st.session_state.board['match']['score']) >= 2 else '')}</td>" if max_sets >= 3 else ""}
        {f"<td>{st.session_state.board['match']['score'][3]['A'] if len(st.session_state.board['match']['score'])>=4 else (st.session_state.board['match']['games']['A'] if len(st.session_state.board['match']['score']) >= 3 else '')}</td>" if max_sets >= 4 else ""}
        {f"<td>{st.session_state.board['match']['score'][4]['A'] if len(st.session_state.board['match']['score'])>=5 else (st.session_state.board['match']['games']['A'] if len(st.session_state.board['match']['score']) >= 4 else '')}</td>" if max_sets >= 5 else ""}
        <td>{st.session_state.board['match']['points']['A']}</td>
    </tr>
    <tr>
        <td><b>{f"{st.session_state.board['teams']['B']['player_1']}{'🟡' if st.session_state.board['serving']['current'] == 'B1' else ''}<br>{st.session_state.board['teams']['B']['player_2']}{'🟡' if st.session_state.board['serving']['current'] == 'B2' else ''}"}</b></td>
        {f"<td>{st.session_state.board['match']['score'][0]['B'] if len(st.session_state.board['match']['score']) >= 1 else (st.session_state.board['match']['games']['B'] if len(st.session_state.board['match']['score']) >= 0 else '')}</td>" if max_sets >= 1 else ""}
        {f"<td>{st.session_state.board['match']['score'][1]['B'] if len(st.session_state.board['match']['score']) >= 2 else (st.session_state.board['match']['games']['B'] if len(st.session_state.board['match']['score']) >= 1 else '')}</td>" if max_sets >= 2 else ""}
        {f"<td>{st.session_state.board['match']['score'][2]['B'] if len(st.session_state.board['match']['score']) >= 3 else (st.session_state.board['match']['games']['B'] if len(st.session_state.board['match']['score']) >= 2 else '')}</td>" if max_sets >= 3 else ""}
        {f"<td>{st.session_state.board['match']['score'][3]['B'] if len(st.session_state.board['match']['score']) >= 4 else (st.session_state.board['match']['games']['B'] if len(st.session_state.board['match']['score']) >= 3 else '')}</td>" if max_sets >= 4 else ""}
        {f"<td>{st.session_state.board['match']['score'][4]['B'] if len(st.session_state.board['match']['score']) >= 5 else (st.session_state.board['match']['games']['B'] if len(st.session_state.board['match']['score']) >= 4 else '')}</td>" if max_sets >= 5 else ""}
        <td>{st.session_state.board['match']['points']['B']}</td>
    </tr>
</table>
""".replace("\n", "").replace("\t", "").replace("  ", "")
st.markdown(score_table_html, unsafe_allow_html=True)

def no_point_details():
    for player in ["A1", "A2", "B1", "B2"]:
        st.session_state.board["live_stats"][player].append(0)
    st.rerun()

@st.dialog("Statistiques", width="medium", dismissible=True, on_dismiss=no_point_details)
def point_details(team):
    winner, loser = team, "A" if team == "B" else "B"
    players = ["A1", "A2", "B1", "B2"]
    st.markdown("### Comment a fini le point ?")
    col_g1, col_d1 = st.columns(2)
    _, col_c, _ = st.columns(3)
    col_g2, col_d2 = st.columns(2)
    with col_g1:
        if st.button(f"💪 Coup gagnant de {st.session_state.board['teams'][winner]['player_1']}"):
            for player in players:
                if player == f"{winner}1":
                    st.session_state.board["live_stats"][player].append(1)
                else:
                    st.session_state.board["live_stats"][player].append(0)
            st.rerun()
    with col_d1:
        if st.button(f"💪 Coup gagnant {st.session_state.board['teams'][winner]['player_2']}"):
            for player in players:
                if player == f"{winner}2":
                    st.session_state.board["live_stats"][player].append(1)
                else:
                    st.session_state.board["live_stats"][player].append(0)
            st.rerun()
    with col_c:
        if st.button("🟰 Faute provoquée"):
            for player in players:
                st.session_state.board["live_stats"][player].append(0)
            st.rerun()
    with col_g2:
        if st.button(f"❌ Faute directe {st.session_state.board['teams'][loser]['player_1']}"):
            for player in players:
                if player == f"{loser}1":
                    st.session_state.board["live_stats"][player].append(-1)
                else:
                    st.session_state.board["live_stats"][player].append(0)
            st.rerun()
    with col_d2:
        if st.button(f"❌ Faute directe {st.session_state.board['teams'][loser]['player_2']}"):
            for player in players:
                if player == f"{loser}2":
                    st.session_state.board["live_stats"][player].append(-1)
                else:
                    st.session_state.board["live_stats"][player].append(0)
            st.rerun()

# ✅ Zones d’action (boutons)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### {st.session_state.board['teams']['A']['name']}")
    if st.button("✅ Point gagné", key="point_A"):
        point_won(st.session_state.board, "A")
        if st.session_state.board["follow_players_stats"]:
            point_details("A")
        else:
            st.rerun()
with col2:
    st.markdown(f"### {st.session_state.board['teams']['B']['name']}")
    if st.button("✅ Point gagné", key="point_B"):
        point_won(st.session_state.board, "B")
        if st.session_state.board["follow_players_stats"]:
            point_details("B")
        else:
            st.rerun()
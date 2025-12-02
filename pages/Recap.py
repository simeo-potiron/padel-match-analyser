# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
import pandas as pd
import json
import uuid
import time

# Streamlit Package
import streamlit as st

# Datetime Packages
from datetime import datetime

# Plotly Packages
import plotly.graph_objects as go


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
st.set_page_config(page_title="Recap match", page_icon="📊", layout="wide")


# ~~~~    Initial checks    ~~~~ #
require_login()
if "match_id" not in st.session_state or st.session_state.match_id is None:
    st.switch_page("Home.py")
elif any([el not in st.session_state or st.session_state[el] is None for el in SESSION_STATE_MATCH_FIELDS]):
    st.switch_page("Home.py")


# ~~~~    Global HTML settings    ~~~~ #
st.markdown("""
<style>
    table {
        text-align: center !important;
        font-size: 1.4rem !important;
        width: 100%;
        border-collapse: collapse;
        color: white;
        border-radius: 10px;
        overflow: hidden;
    }
    .result-container {
        background: linear-gradient(135deg, #0047ab, #0074ff);
        color: white;
        padding: 40px;
        border-radius: 18px;
        text-align: center;
        font-size: 24px;
        width: 90%;
        margin: auto;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
    }
    .result-title {
        font-size: 38px;
        font-weight: 900;
        margin-bottom: 15px;
    }
    .result-score {
        font-size: 30px;
        font-weight: 700;
        margin-top: 10px;
    }
    .players {
        font-size: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ~~~~    Pop-Up functions    ~~~~ #
# Pop-Up: Pending changes 
@st.dialog("🚨 Modifications non sauvegardées", width="small", dismissible=False)
def go_home():
    st.write("Voulez-vous vraiment quitter la page ?")
    st.write("Des données non sauvegardées seront perdues...")
    st.space("small")
    vide_1, yes_col, vide_2, no_col, vide_3 = st.columns(5)
    with yes_col: 
        if st.button("Oui"):
            st.switch_page("Home.py")
    with no_col:
        if st.button("Non"):
            st.rerun()

# Pop-Up: Share match
@st.dialog("Partager ce match", width="small", dismissible=True, on_dismiss="rerun")
def share_match():
    current_viewers_ids = [user.get("token") for user in st.session_state.match_viewers]
    current_viewers = [user.get("email") for user in st.session_state.match_viewers if user.get("token") != st.session_state.token]
    if current_viewers:
        # Display current players
        st.markdown("""
        <style>
        .scroll-container {
            display: flex;
            overflow-x: auto;
            white-space: nowrap;
            gap: 1rem;
        }
        .item {
            background: #eee;
            color: black;
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
            flex: 0 0 auto;
        }
        </style>""", unsafe_allow_html=True)
        scroller = "<div class='scroll-container'>"
        for user in current_viewers:
            scroller += f"<div class='item'>{user}</div>"
        scroller += "</div>"
        st.write("Présents sur ce match:")
        st.markdown(scroller, unsafe_allow_html=True)
        st.space("small")
    # Add new players
    available_users = get_other_users(current_viewers_ids)
    if available_users:
        to_invite = st.multiselect("Inviter sur ce match:", [user.get("email") for user in available_users])
        if st.button("Ajouter au match") and to_invite:
            new_viewers_ids = [user.get("token") for user in available_users if user.get("email") in to_invite]
            upsert_match("update", match_id=st.session_state.match_id, match_hash={"viewers": current_viewers_ids + new_viewers_ids})
            st.success(f"{len(new_viewers_ids)} nouveaux joueurs ajoutés au match")
            time.sleep(2)
            st.rerun()

# Pop-Up: Save changes
@st.dialog("Détails de la partie:", width="small", dismissible=True, on_dismiss="rerun")
def save_match(display_score):
    default_name = st.session_state.match_name or "Match entre copains"
    default_date = st.session_state.match_date or datetime.today().strftime('%Y-%m-%d')
    name_col, date_col = st.columns(2)
    with name_col:
        name = st.text_input("Nommer la partie:", value=default_name, label_visibility="collapsed")
    with date_col:
        date = st.date_input("Date de la partie:", value=default_date, max_value="today", label_visibility="collapsed")
    if st.button("💾"):
        if name and date:
            match_hash = {"name": name, "date": date.strftime('%Y-%m-%d'), "display_score": display_score, "board": json.dumps(st.session_state.match_board)}
            upsert_match("update", match_id=st.session_state.match_id, match_hash=match_hash)
            del st.session_state["matches"] # Remove matches from the session to rescan them
            st.success("Match enregistré avec succès")
            time.sleep(2)
            st.switch_page("Home.py")
        else:
            st.error("Merci de renseigner un nom et une date pour enregistrer cette partie")


# ~~~~    Page core    ~~~~ #
# Header
title_col, share_col, home_col = st.columns([8,1,1])
with title_col:
    st.title("Resultats")
with share_col:
    st.space("small")
    if st.button("📤 Share"):
        share_match()
    st.space("small")
with home_col:
    st.space("small")
    if st.button("🏠 Home"):
        if st.session_state.match_updated:
            go_home()
        else:
            st.switch_page("Home.py")
    st.space("small")

# Store the winner of the match
winner = st.session_state.match_board["winner"]
match_over = winner in ["A", "B"]

# Match result band:
if match_over:
    # Display match result
    team_name = st.session_state.match_board["teams"][winner]["name"]
    final_sets = " ".join([f"{set_score['A']}/{set_score['B']}" for set_score in st.session_state.match_board["match"]["score"]])
    st.markdown(f"""
    <div class="result-container">
    <div class="result-title">🏆 Jeu, Set et Match !</div>
    <div class="players">Victoire de <strong>{team_name}</strong> !</div>
    <div class="result-score">Score final : <strong>{final_sets}</strong></div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display current match state
    team_name_a = st.session_state.match_board["teams"]["A"]["name"]
    team_name_b = st.session_state.match_board["teams"]["B"]["name"]
    final_sets = " ".join(
        [f"{set_score['A']}/{set_score['B']}" for set_score in st.session_state.match_board["match"]["score"]] +
        [f"{st.session_state.match_board['match']['games']['A']}/{st.session_state.match_board['match']['games']['B']}"] +
        [f"{st.session_state.match_board['match']['points']['A']}-{st.session_state.match_board['match']['points']['B']}"]
    )
    st.markdown(f"""
    <div class="result-container">
    <div class="result-title"> 🚧 Match interrompu !</div>
    <div class="players"><strong>{team_name_a}</strong> VS <strong>{team_name_b}</strong>:</div>
    <div class="result-score"><strong>{final_sets}</strong></div>
    </div>
    """, unsafe_allow_html=True)
st.space("small")

# Initiate recap_display
if "recap_display" not in st.session_state:
    st.session_state.recap_display = {
        "match": 0,
        "players": 0,
        "video": 0
    }

# Allow user to change view
match_button, player_button, video_button, _, return_button, save_button = st.columns([2, 2, 2, 3, 3, 3])
with match_button:
    if st.button("Match stats"):
        st.session_state.recap_display = {
            "match": (st.session_state.recap_display["match"]+1)%2, 
            "players": 0,
            "video": 0
        }
        st.rerun()
with player_button:
    if st.session_state.match_board["follow_players_stats"]:
        if st.button("Players stats"):
            st.session_state.recap_display = {
                "match": 0, 
                "players": (st.session_state.recap_display["players"]+1)%2,
                "video": 0
            }
            st.rerun()
with video_button:
    if st.button("Match video"):
        st.session_state.recap_display = {
            "match": 0, 
            "players": 0,
            "video": (st.session_state.recap_display["video"]+1)%2
        }
        st.rerun()
with return_button:
    if st.session_state.match_admin:
        if not match_over:
            # ⏯️ Restart pending match
            if st.button("⏯️ Reprendre le match"):
                st.session_state.match_board["winner"] = None
                st.switch_page("pages/Match.py")
        else:
            # ❌ Reset last point and restart match
            if st.button("❌ Annuler le dernier point"):
                if undo_point_won(st.session_state.match_board):
                    st.session_state.match_updated = True
                    st.switch_page("pages/Match.py")
with save_button:
    # Display Save button only if needed
    if st.session_state.match_updated and st.session_state.match_admin:
        if st.button("💾 Enregistrer la partie"):
            save_match(final_sets)
                
# Switch display between Match stats, Players stats and Match video
if st.session_state.recap_display["match"] == 1:
    # Title
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Statistiques du match</h2>",
        unsafe_allow_html=True
    )

    # Teams
    st.markdown("""
    <style>
    .team-container {
        background-color: #2c2c2c;
        border-radius: 15px;
        padding: 2vh 3vw;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Arial';
        width: 100%;
    }

    .team-block {
        color: white;
        font-size: 24px;
        font-weight: 800;
        line-height: 1.5;
    }

    .team-block div {
        margin: 5px 0;
    }

    .vs-block {
        background-color: white;
        color: black;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="team-container">
        <div class="team-block">
            <div>{st.session_state.match_board["teams"]["A"]["player_1"]}</div>
            <div>{st.session_state.match_board["teams"]["A"]["player_2"]}</div>
        </div>
        <div class="vs-block">VS</div>
        <div class="team-block" style="text-align: right;">
            <div>{st.session_state.match_board["teams"]["B"]["player_1"]}</div>
            <div>{st.session_state.match_board["teams"]["B"]["player_2"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Selectbox Mat/Set_n
    _, select_box_col = st.columns([8,2])
    with select_box_col:
        nb_sets_played = len(st.session_state.match_board["match"]["score"]) + (0 if match_over else 1)
        options = ["Match"] + [f"Set{k+1}" for k in range(nb_sets_played)]
        period = st.selectbox(
            label="Period considered",
            options=options,
            label_visibility="hidden",
        )

    # Display global stats:
    data = {
        "A": [], 
        "Stat": [
            "Balles de match", 
            "Balles de break jouées",
            "Balles de break converties",
            "Total de points gagnés",
            "Points gagnés au service", 
            "Points gagnés au retour",
            "Points gagnants",
            "Fautes directes"
        ], 
        "B": []
    }
    live_stats = st.session_state.match_board["live_stats"]
    ## Filter data only on the selected period
    if period == "Match":
        stats = pd.DataFrame(live_stats)
    else:
        set_number = int(period[-1])
        first_idx = live_stats["events"].index(f"Fin set {set_number - 1}") + 1 if set_number > 1 else 0
        last_idx = live_stats["events"].index(f"Fin set {set_number}") + 1 if set_number < nb_sets_played else None
        stats = pd.DataFrame(live_stats)[first_idx:last_idx]
    ## Match points
    data["A"].append(f"{stats[stats.match_points == 'A'].shape[0]}")
    data["B"].append(f"{stats[stats.match_points == 'B'].shape[0]}")
    ## Break points
    data["A"].append(f"{stats[stats.break_points == 'A'].shape[0]}")
    data["B"].append(f"{stats[stats.break_points == 'B'].shape[0]}")
    ## Breaks
    data["A"].append(f"{stats[stats.breaks == 'A'].shape[0]}")
    data["B"].append(f"{stats[stats.breaks == 'B'].shape[0]}")
    ## Points won
    total_points, points_A, points_B = stats.shape[0], stats[stats.points_won == 'A'].shape[0], stats[stats.points_won == 'B'].shape[0]
    data["A"].append(f"{round(points_A/total_points*100) if total_points > 0 else 0}% ({points_A}/{total_points})")
    data["B"].append(f"{round(points_B/total_points*100) if total_points > 0 else 0}% ({points_B}/{total_points})")
    ## Service/Return points won
    total_points_A, points_AA, points_AB = stats[stats.serving.isin(['A1', 'A2'])].shape[0], stats[stats.serving.isin(['A1', 'A2']) & (stats.points_won == 'A')].shape[0], stats[stats.serving.isin(['A1', 'A2']) & (stats.points_won == 'B')].shape[0]
    total_points_B, points_BB, points_BA = stats[stats.serving.isin(['B1', 'B2'])].shape[0], stats[stats.serving.isin(['B1', 'B2']) & (stats.points_won == 'B')].shape[0], stats[stats.serving .isin(['B1', 'B2']) & (stats.points_won == 'A')].shape[0]
    ### Serve
    data["A"].append(f"{round(points_AA/total_points_A*100) if total_points_A > 0 else 0}% ({points_AA}/{total_points_A})")
    data["B"].append(f"{round(points_BB/total_points_B*100) if total_points_B > 0 else 0}% ({points_BB}/{total_points_B})")
    ### Return
    data["A"].append(f"{round(points_BA/total_points_B*100) if total_points_B > 0 else 0}% ({points_BA}/{total_points_B})")
    data["B"].append(f"{round(points_AB/total_points_A*100) if total_points_A > 0 else 0}% ({points_AB}/{total_points_A})")
    ### Winners
    data["A"].append(f"{stats[(stats.A1 == 1) | (stats.A2 == 1)].shape[0]}")
    data["B"].append(f"{stats[(stats.B1 == 1) | (stats.B2 == 1)].shape[0]}")
    ### Unforced errors
    data["A"].append(f"{stats[(stats.A1 == -1) | (stats.A2 == -1)].shape[0]}")
    data["B"].append(f"{stats[(stats.B1 == -1) | (stats.B2 == -1)].shape[0]}")

    # Highligh external borders depending on the values
    def border_style(row_index, data):
        styles = [''] * df.shape[1]  # init vide pour chaque cellule
        if int(data["B"][row_index].split("%")[0]) > int(data["A"][row_index].split("%")[0]):
            styles[0:-1] = ['border-left: none; border-right: none'] * (len(styles) - 1)
            styles[-1] += 'border-left: none; border-right: 5px solid #f1c40f;'
        elif int(data["A"][row_index].split("%")[0]) > int(data["B"][row_index].split("%")[0]):
            styles[1:] = ['border-left: none; border-right: none'] * (len(styles) - 1)
            styles[0] += 'border-left: 5px solid #f1c40f; border-right: none;'
        else:
            styles = ['border-left: none; border-right: none'] * len(styles)
        return styles
    
    # Shape table using Styler
    df = pd.DataFrame(data)
    styled_df = (
        df.style
            .hide(axis="index")
            .hide(axis="columns")
            .set_table_styles([
                {
                    "selector": "table",
                    "props": [
                        ("display", "inline-table"),
                        ("border-collapse", "collapse"),
                        ("font-size", "18px"),
                        ("background-color", "#111"),
                        ("color", "white"),
                        ("border-radius", "10px"),
                        ("overflow", "hidden"),
                        ("text-align", "center"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("padding", "10px 15px"),
                        ("border-bottom", "1px solid #333"),
                        ("border-top", "none"),
                        ("text-align", "center"),
                        ("vertical-align", "middle"),
                    ],
                },
                {
                    "selector": "tr:last-child td",
                    "props": [("border-bottom", "none")],
                },
                
            ])
    )

    # Apply line style
    styled_df = styled_df.apply(lambda row: border_style(row.name, data), axis=1)
    # Display generated HMTL table
    st.write(styled_df.to_html(), unsafe_allow_html=True)

elif st.session_state.recap_display["players"] == 1:
    # Title
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Statistiques des joueurs</h2>",
        unsafe_allow_html=True
    )

    # Selectbox Mat/Set n
    _, select_box_col = st.columns([8,2])
    with select_box_col:
        nb_sets_played = len(st.session_state.match_board["match"]["score"]) + (0 if match_over else 1)
        options = ["Match"] + [f"Set{k+1}" for k in range(nb_sets_played)]
        period = st.selectbox(
            label="Period considered",
            options=options,
            label_visibility="hidden",
        )

    live_stats = st.session_state.match_board["live_stats"]
    ## Filter data on the selected period
    if period == "Match":
        stats = pd.DataFrame(live_stats)
    else:
        set_number = int(period[-1])
        first_idx = live_stats["events"].index(f"Fin set {set_number - 1}") + 1 if set_number > 1 else 0
        last_idx = live_stats["events"].index(f"Fin set {set_number}") + 1 if set_number < nb_sets_played else None
        stats = pd.DataFrame(live_stats)[first_idx:last_idx]
    
    # Split the screen: display the graph (left) and the table (right)
    graph_col, tab_col = st.columns([2,1])
    fig = go.Figure()
    # Display players stats in a timeline
    players_stats = {
        str(st.session_state.match_board["teams"]["A"]["player_1"]): stats.A1, #st.session_state.match_board["live_stats"]["A1"],
        str(st.session_state.match_board["teams"]["A"]["player_2"]): stats.A2, #st.session_state.match_board["live_stats"]["A2"],
        str(st.session_state.match_board["teams"]["B"]["player_1"]): stats.B1, #st.session_state.match_board["live_stats"]["B1"],
        str(st.session_state.match_board["teams"]["B"]["player_2"]): stats.B2, #st.session_state.match_board["live_stats"]["B2"],
    }
    df_raw = pd.DataFrame(players_stats)
    df_cum = df_raw.cumsum()
    # Choose flashy colors to display the lines
    colors = [
        "#FFFF00",  # jaune flashy
        "#FFA500",  # orange flashy
        "#00FFFF",  # cyan clair
        "#fa25cb"   # rose vif
    ]
    # Add each line to the graph
    for i, col in enumerate(df_cum.columns):
        color = colors[i]
        fig.add_trace(go.Scatter(
            x=df_cum.index - df_cum.index[0],
            y=df_cum[col],
            mode='lines',
            name=f'<span style="color:{color}"><b>{col}</b></span>',
            line=dict(shape='hvh', color=color)
        ))
    
    # --- Display match events on the graph ---
    events_labels = [x if x != 0 else "" for x in stats.events]
    label_positions = [i for i, txt in enumerate(events_labels) if txt != ""]
    label_texts = [txt for txt in events_labels if txt != ""]
    y_for_labels = [0]*len(label_positions)
    fig.add_trace(go.Scatter(
        x=label_positions,
        y=y_for_labels,
        mode="markers+text",
        text=label_texts,
        textposition="top center",
        marker=dict(size=12, color="white", line=dict(color="black", width=2)),
        showlegend=False
    ))

    # Shape and style of the graph
    fig.update_layout(
        title="Evolution des joueurs - ratio Points gagnants / Fautes directes",
        xaxis=dict(visible=False),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            title="",
            font=dict(size=12),
        ),
        margin=dict(b=100)
    )
    # Display chart in Streamlit
    with graph_col:
        st.plotly_chart(fig, width="stretch")

    # Display players stats in a table (Winners  and Unforced errors)
    data = {
        "Points gagnants": [sum([1 if x == 1 else 0 for x in stats[player]]) for player in ["A1", "A2", "B1", "B2"]], 
        "Joueur": [st.session_state.match_board["teams"][player[0]][f"player_{player[1]}"] for player in ["A1", "A2", "B1", "B2"]], 
        "Fautes directes": [sum([1 if x == -1 else 0 for x in stats[player]]) for player in ["A1", "A2", "B1", "B2"]]
    }
    df = pd.DataFrame(data)
    styled_df = (
        df.style
            .hide(axis="index")
            .set_table_styles([
                {
                    "selector": "table",
                    "props": [
                        ("display", "inline-table"),
                        ("border-collapse", "collapse"),
                        ("font-size", "12px"),
                        ("background-color", "#111"),
                        ("color", "white"),
                        ("border-radius", "10px"),
                        ("overflow", "hidden"),
                        ("text-align", "center"),
                    ],
                },
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#222"),
                        ("color", "white"),
                        ("padding", "12px 15px"),
                        ("font-size", "15px"),
                        ("font-weight", "bold"),
                        ("border-bottom", "2px solid #444"),
                        ("border-top", "none"),
                        ("border-left", "none"),
                        ("border-right", "none"),
                        ("text-align", "center"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("padding", "10px 15px"),
                        ("font-size", "15px"),
                        ("border-bottom", "1px solid #333"),
                        ("border-top", "none"),
                        ("border-left", "none"),
                        ("border-right", "none"),
                        ("text-align", "center"),
                        ("vertical-align", "middle"),
                    ],
                },
                {
                    "selector": "tr:last-child td",
                    "props": [("border-bottom", "none")],
                },
                
            ])
    )
    with tab_col:
        st.space(size="large")
        st.space(size="small")
        st.write(styled_df.to_html(), unsafe_allow_html=True)

elif st.session_state.recap_display["video"] == 1:
    # Title
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Vidéo du match</h2><br>",
        unsafe_allow_html=True
    )
    # Display video
    l, c, r = st.columns([1,3,1])
    with c:
        if st.session_state.match_video:
            st.video(st.session_state.match_video)
        if "file_uploader_key" not in st.session_state:
            st.session_state.file_uploader_key = "file_uploader_0"
        if st.session_state.match_admin:
            new_video = st.file_uploader("Lier une nouvelle vidéo à ce match:", type=["mp4", "mov"], key=st.session_state.file_uploader_key)
            if new_video:
                public_video_url = store_video_to_gcs(new_video)
                if st.session_state.match_video:
                    delete_video_from_gcs(st.session_state.match_video)
                st.session_state.match_video = public_video_url
                upsert_match("update", match_id=st.session_state.match_id, match_hash={"video": public_video_url})
                st.session_state.file_uploader_key = f"file_uploader_{uuid.uuid4()}"
                st.rerun()

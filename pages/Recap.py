import streamlit as st
import pandas as pd
import datetime as dt
import json
import uuid
import plotly.graph_objects as go
from utils import require_login, upsert_match, get_match_data, store_video_to_gcs, delete_video_from_gcs

st.set_page_config(page_title="Recap match", page_icon="📊", layout="wide")
require_login()

# ✅ Style mobile
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

title_col, new_col = st.columns([8,2])
with title_col:
    st.title("Resultats")
with new_col:
    st.space("small")
    if st.button("🏠 Home"):
        st.switch_page("Home.py")
    st.space("small")

try:
    # Vérifie que board ait bien été initialisé et que le match est bien stocké en base
    if st.session_state.board is None or st.session_state.match_id is None:
        raise Exception
except:
    st.switch_page("Home.py")

winner = st.session_state.board["winner"]
match_over = winner in ["A", "B"]

# Match result band:
if match_over:
    # Display match result
    team_name = st.session_state.board["teams"][winner]["name"]
    final_sets = " ".join([f"{set_score['A']}/{set_score['B']}" for set_score in st.session_state.board["match"]["score"]])

    st.markdown(f"""
    <div class="result-container">
    <div class="result-title">🏆 Jeu, Set et Match !</div>
    <div class="players">Victoire de <strong>{team_name}</strong> !</div>
    <div class="result-score">Score final : <strong>{final_sets}</strong></div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display current match state
    team_name_a = st.session_state.board["teams"]["A"]["name"]
    team_name_b = st.session_state.board["teams"]["B"]["name"]
    final_sets = " ".join(
        [f"{set_score['A']}/{set_score['B']}" for set_score in st.session_state.board["match"]["score"]] +
        [f"{st.session_state.board['match']['games']['A']}/{st.session_state.board['match']['games']['B']}"] +
        [f"{st.session_state.board['match']['points']['A']}-{st.session_state.board['match']['points']['B']}"]
    )

    st.markdown(f"""
    <div class="result-container">
    <div class="result-title"> 🚧 Match interrompu !</div>
    <div class="players"><strong>{team_name_a}</strong> VS <strong>{team_name_b}</strong>:</div>
    <div class="result-score"><strong>{final_sets}</strong></div>
    </div>
    """, unsafe_allow_html=True)
st.write("")

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
    if st.session_state.board["follow_players_stats"]:
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
    if not match_over:
        # ⏯️ Bouton pour reprendre le match
        if st.button("⏯️ Reprendre le match"):
            st.session_state.board["winner"] = None
            st.switch_page("pages/Match.py")
with save_button:
    @st.dialog("Détails de la partie:", width="small", dismissible=True, on_dismiss="rerun")
    def save_match():
        default_name = get_match_data(st.session_state.match_id, "name") or "Match entre copains"
        default_date = get_match_data(st.session_state.match_id, "date") or dt.datetime.today().strftime('%Y-%m-%d')
        name_col, date_col = st.columns(2)
        with name_col:
            name = st.text_input("Nommer la partie:", value=default_name, label_visibility="collapsed")
        with date_col:
            date = st.date_input("Date de la partie:", value=default_date, max_value="today", label_visibility="collapsed")
        if st.button("💾"):
            if name and date:
                match_hash = {"name": name, "date": date.strftime('%Y-%m-%d'), "board": json.dumps(st.session_state.board)}
                upsert_match("update", match_id=st.session_state.match_id, match_hash=match_hash)
                st.switch_page("Home.py")
            else:
                st.error("Merci de renseigner un nom et une date pour enregistrer cette partie")

    if st.button("💾 Enregistrer la partie"):
        save_match()
                

# Switch display between Match stats, Players stats and Match video
if st.session_state.recap_display["match"] == 1:
    # Titre
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Statistiques du match</h2>",
        unsafe_allow_html=True
    )

    # Paires
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
            <div>{st.session_state.board["teams"]["A"]["player_1"]}</div>
            <div>{st.session_state.board["teams"]["A"]["player_2"]}</div>
        </div>
        <div class="vs-block">VS</div>
        <div class="team-block" style="text-align: right;">
            <div>{st.session_state.board["teams"]["B"]["player_1"]}</div>
            <div>{st.session_state.board["teams"]["B"]["player_2"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Selectbox Mat/Set n
    _, select_box_col = st.columns([8,2])
    with select_box_col:
        nb_sets_played = len(st.session_state.board["match"]["score"]) + (0 if match_over else 1)
        options = ["Match"] + [f"Set{k+1}" for k in range(nb_sets_played)]
        period = st.selectbox(
            label="Period considered",
            options=options,
            label_visibility="hidden",
        )

    # Affichage des statistiques globales:
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
    live_stats = st.session_state.board["live_stats"]
    ## Preparer la donnée selon la période considérée
    if period == "Match":
        stats = pd.DataFrame(live_stats)
    else:
        set_number = int(period[-1])
        first_idx = live_stats["events"].index(f"Fin set {set_number - 1}") + 1 if set_number > 1 else 0
        last_idx = live_stats["events"].index(f"Fin set {set_number}") + 1 if set_number < nb_sets_played else None
        stats = pd.DataFrame(live_stats)[first_idx:last_idx]
    ## Balles de macth
    data["A"].append(f"{stats[stats.match_points == 'A'].shape[0]}")
    data["B"].append(f"{stats[stats.match_points == 'B'].shape[0]}")
    ## Balles de break
    data["A"].append(f"{stats[stats.break_points == 'A'].shape[0]}")
    data["B"].append(f"{stats[stats.break_points == 'B'].shape[0]}")
    ## Breaks
    data["A"].append(f"{stats[stats.breaks == 'A'].shape[0]}")
    data["B"].append(f"{stats[stats.breaks == 'B'].shape[0]}")
    ## Points gagnés
    total_points, points_A, points_B = stats.shape[0], stats[stats.points_won == 'A'].shape[0], stats[stats.points_won == 'B'].shape[0]
    data["A"].append(f"{round(points_A/total_points*100) if total_points > 0 else 0}% ({points_A}/{total_points})")
    data["B"].append(f"{round(points_B/total_points*100) if total_points > 0 else 0}% ({points_B}/{total_points})")
    ## Points gagnés au service et au retour
    total_points_A, points_AA, points_AB = stats[stats.serving.isin(['A1', 'A2'])].shape[0], stats[stats.serving.isin(['A1', 'A2']) & (stats.points_won == 'A')].shape[0], stats[stats.serving.isin(['A1', 'A2']) & (stats.points_won == 'B')].shape[0]
    total_points_B, points_BB, points_BA = stats[stats.serving.isin(['B1', 'B2'])].shape[0], stats[stats.serving.isin(['B1', 'B2']) & (stats.points_won == 'B')].shape[0], stats[stats.serving .isin(['B1', 'B2']) & (stats.points_won == 'A')].shape[0]
    ### Serve
    data["A"].append(f"{round(points_AA/total_points_A*100) if total_points_A > 0 else 0}% ({points_AA}/{total_points_A})")
    data["B"].append(f"{round(points_BB/total_points_B*100) if total_points_B > 0 else 0}% ({points_BB}/{total_points_B})")
    ### Return
    data["A"].append(f"{round(points_BA/total_points_B*100) if total_points_B > 0 else 0}% ({points_BA}/{total_points_B})")
    data["B"].append(f"{round(points_AB/total_points_A*100) if total_points_A > 0 else 0}% ({points_AB}/{total_points_A})")
    ### Points gagnants
    data["A"].append(f"{stats[(stats.A1 == 1) | (stats.A2 == 1)].shape[0]}")
    data["B"].append(f"{stats[(stats.B1 == 1) | (stats.B2 == 1)].shape[0]}")
    ### Fautes directes
    data["A"].append(f"{stats[(stats.A1 == -1) | (stats.A2 == -1)].shape[0]}")
    data["B"].append(f"{stats[(stats.B1 == -1) | (stats.B2 == -1)].shape[0]}")

    # Fonction pour styliser les lignes en indiquant le plus grand
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
    
    # ✅ Stylisation directe via Styler
    df = pd.DataFrame(data)
    styled_df = (
        df.style
            .hide(axis="index")
            .hide(axis="columns")
            .set_table_styles([
                # Table globale
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
                # Cellules
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
                # Dernière ligne sans bordure
                {
                    "selector": "tr:last-child td",
                    "props": [("border-bottom", "none")],
                },
                
            ])
    )

    # Appliquer le style à chaque ligne
    styled_df = styled_df.apply(lambda row: border_style(row.name, data), axis=1)
    # # Affichage direct du HTML généré
    st.write(styled_df.to_html(), unsafe_allow_html=True)

elif st.session_state.recap_display["players"] == 1:
    # Titre
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Statistiques des joueurs</h2>",
        unsafe_allow_html=True
    )

    # Selectbox Mat/Set n
    _, select_box_col = st.columns([8,2])
    with select_box_col:
        nb_sets_played = len(st.session_state.board["match"]["score"]) + (0 if match_over else 1)
        options = ["Match"] + [f"Set{k+1}" for k in range(nb_sets_played)]
        period = st.selectbox(
            label="Period considered",
            options=options,
            label_visibility="hidden",
        )

    live_stats = st.session_state.board["live_stats"]
    ## Preparer la donnée selon la période considérée
    if period == "Match":
        stats = pd.DataFrame(live_stats)
    else:
        set_number = int(period[-1])
        first_idx = live_stats["events"].index(f"Fin set {set_number - 1}") + 1 if set_number > 1 else 0
        last_idx = live_stats["events"].index(f"Fin set {set_number}") + 1 if set_number < nb_sets_played else None
        stats = pd.DataFrame(live_stats)[first_idx:last_idx]
    
    # Séparation de l'écran entre graph à gauche et table à droite
    graph_col, tab_col = st.columns([2,1])
 
    fig = go.Figure() # Création de la figure
    # --- Trace pour les valeurs des joueurs ---
    # Affichage des statistiques des joueurs au cours du match:
    players_stats = {
        str(st.session_state.board["teams"]["A"]["player_1"]): stats.A1, #st.session_state.board["live_stats"]["A1"],
        str(st.session_state.board["teams"]["A"]["player_2"]): stats.A2, #st.session_state.board["live_stats"]["A2"],
        str(st.session_state.board["teams"]["B"]["player_1"]): stats.B1, #st.session_state.board["live_stats"]["B1"],
        str(st.session_state.board["teams"]["B"]["player_2"]): stats.B2, #st.session_state.board["live_stats"]["B2"],
    }
    df_raw = pd.DataFrame(players_stats)
    df_cum = df_raw.cumsum() # Somme cumulée
    # 🎨 Couleurs flashy (néon / saturées)
    colors = [
        "#FFFF00",  # jaune flashy
        "#FFA500",  # orange flashy
        "#00FFFF",  # cyan clair
        "#fa25cb"   # rose vif
    ]
    # Ajouter la ligne au graph
    for i, col in enumerate(df_cum.columns):
        color = colors[i]
        # Trace avec légende colorée et ligne en escalier
        fig.add_trace(go.Scatter(
            x=df_cum.index - df_cum.index[0],
            y=df_cum[col],
            mode='lines',
            name=f'<span style="color:{color}"><b>{col}</b></span>',  # texte coloré
            line=dict(shape='hvh', color=color),
            # legendgroup=col
        ))
    
    # --- Trace pour les evenements ---
    # On isole les positions où il y a un texte
    events_labels = [x if x != 0 else "" for x in stats.events]
    label_positions = [i for i, txt in enumerate(events_labels) if txt != ""]
    label_texts = [txt for txt in events_labels if txt != ""]
    y_for_labels = [0]*len(label_positions)
    # On ajoute les labels au graph
    fig.add_trace(go.Scatter(
        x=label_positions,
        y=y_for_labels,
        mode="markers+text",
        text=label_texts,
        textposition="top center",
        marker=dict(size=12, color="white", line=dict(color="black", width=2)),
        showlegend=False
    ))

    # Mise en forme du graphique
    fig.update_layout(
        title="Evolution des joueurs - ratio Points gagnants / Fautes directes",
        xaxis=dict(visible=False), # Cache l'axe des abscisses
        legend=dict(
            orientation="h",        # Légende horizontale
            yanchor="top",          # Alignement vertical
            y=-0.25,                # Placement sous le graphique
            xanchor="center",       # Centrage horizontal
            x=0.5,                  # Position centrale
            title="",               # Pas de titre de légende
            font=dict(size=12),
        ),
        margin=dict(b=100)  # Laisse un peu d’espace pour la légende en bas
    )
    # Affichage dans Streamlit
    with graph_col:
        st.plotly_chart(fig, width="stretch")

    # Affichage des stats Points gagnants / Fautes directes totales par joueur
    data = {
        "Points gagnants": [sum([1 if x == 1 else 0 for x in stats[player]]) for player in ["A1", "A2", "B1", "B2"]], 
        "Joueur": [st.session_state.board["teams"][player[0]][f"player_{player[1]}"] for player in ["A1", "A2", "B1", "B2"]], 
        "Fautes directes": [sum([1 if x == -1 else 0 for x in stats[player]]) for player in ["A1", "A2", "B1", "B2"]]
    }
    df = pd.DataFrame(data)
    styled_df = (
        df.style
            .hide(axis="index")
            .set_table_styles([
                # Table globale
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
                # Header
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
                # Cellules
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
                # Dernière ligne sans bordure
                {
                    "selector": "tr:last-child td",
                    "props": [("border-bottom", "none")],
                },
                
            ])
    )
    # Affichage direct du HTML généré
    with tab_col:
        st.space(size="large")
        st.space(size="small")
        st.write(styled_df.to_html(), unsafe_allow_html=True)


elif st.session_state.recap_display["video"] == 1:
    # Titre
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Vidéo du match</h2><br>",
        unsafe_allow_html=True
    )
    video_url = get_match_data(st.session_state.match_id, "video")
    l, c, r = st.columns([1,3,1])
    with c:
        if video_url:
            st.video(video_url)
        if "file_uploader_key" not in st.session_state:
            st.session_state.file_uploader_key = "file_uploader_0"
        new_video = st.file_uploader("Lier une nouvelle vidéo à ce match:", type=["mp4", "mov"], key=st.session_state.file_uploader_key)
        if new_video:
            public_video_url = store_video_to_gcs(new_video)
            if video_url:
                delete_video_from_gcs(video_url)
            upsert_match("update", match_id=st.session_state.match_id, match_hash={"video": public_video_url})
            st.session_state.file_uploader_key = f"file_uploader_{uuid.uuid4()}"
            st.rerun()


        
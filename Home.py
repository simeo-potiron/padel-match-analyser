import streamlit as st
import json

from utils import *

st.set_page_config(page_title="Home", layout="wide")
require_login()

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

title_col, new_col = st.columns([8,2])
with title_col:
    st.title("Mes matchs")
with new_col:
    st.space("small")
    if st.button("➕ Nouveau match"):
        st.session_state.match_id = upsert_match("create", match_hash={"players": [st.session_state["token"]]})["id"]
        if st.session_state.match_id:
            st.switch_page("pages/NewMatch.py")
    st.space("small")

DEFAULT_DISPLAYED_MATCHES = 3
if "match_id" not in st.session_state or st.session_state.match_id is not None:
    st.session_state.match_id = None
    st.session_state.displayed_matches = DEFAULT_DISPLAYED_MATCHES
elif "displayed_matches" not in st.session_state:
    st.session_state.displayed_matches = DEFAULT_DISPLAYED_MATCHES

matches = get_matches(st.session_state["token"])
matches.sort(reverse=True, key=lambda x: x.get("fields").get("date", "") + x.get("fields").get("name", ""))
cmpt = 0
for match in matches[:st.session_state.displayed_matches]:
    cmpt += 1
    with st.container():
        l, r, rr = st.columns([6,2,1])
        try:
            board = json.loads(match.get("fields").get("board"))
            with l:
                if board["winner"] in ["A", "B"]:
                    score = " ".join([f"{set_score['A']}/{set_score['B']}" for set_score in board["match"]["score"]])
                else:
                    score = " ".join(
                        [f"{set_score['A']}/{set_score['B']}" for set_score in board["match"]["score"]] +
                        [f"{board['match']['games']['A']}/{board['match']['games']['B']}"] +
                        [f"{board['match']['points']['A']}-{board['match']['points']['B']}"]
                    )
                st.markdown(
                    f"<h3 style='text-align: left; color: #FFA139;'>{match.get('fields').get('name')}</h3>",
                    unsafe_allow_html=True
                )
                date_col, score_col = st.columns(2)
                with date_col:
                    st.write(f"#### Date: {match.get('fields').get('date')}")
                with score_col:
                    st.write(f"#### Score : {score}")
        except:
            with l:
                st.markdown(f"### {match.get('fields').get('name') or 'Match vide'}")
        finally:
            with r:
                if st.button(f"Ouvrir ce match", key=f"recap_{match.get('id')}"):
                    st.session_state.match_id = match.get("id")
                    st.session_state.board = board
                    st.switch_page("pages/Match.py")
            with rr:
                if st.button(f"🗑️", key=f"delete_{match.get('id')}", type="primary"):
                    match_data = get_match_data(match.get("id"))
                    if len(match_data.get("players")) == 1:
                        match_video = match_data.get("video")
                        if match_video:
                            delete_video_from_gcs(match_video)
                        upsert_match("delete", match_id=match.get("id"))
                    else:
                        new_players = [usr_token for usr_token in match_data.get("players") if usr_token != st.session_state.token]
                        upsert_match("update", match_id=match.get("id"), match_hash={"players": new_players})
                    st.rerun()
            if cmpt == st.session_state.displayed_matches:
                if len(matches) > st.session_state.displayed_matches:
                    l,c,r = st.columns(3)
                    with l:
                        st.markdown("---")
                    with c:
                        st.space(1)
                        if st.button("Afficher plus 🔽", width="stretch"):
                            st.session_state.displayed_matches += DEFAULT_DISPLAYED_MATCHES
                            st.rerun()
                    with r:
                        st.markdown("---")
                else:
                    st.markdown("---")
            else:
                st.markdown("---")
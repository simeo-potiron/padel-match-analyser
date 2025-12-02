# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
import json

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
st.set_page_config(page_title="Home", layout="wide")


# ~~~~    Initial checks    ~~~~ #
require_login()
if "match_id" not in st.session_state or st.session_state.match_id is not None:
    # Initial setting of the number of displayed matches
    st.session_state.displayed_matches = DEFAULT_DISPLAYED_MATCHES
    # Set/Reset session_state match informations
    close_current_match()
    st.rerun()
elif "displayed_matches" not in st.session_state:
    # Initial setting of the number of displayed matches
    st.session_state.displayed_matches = DEFAULT_DISPLAYED_MATCHES
    st.rerun()
if "matches" not in st.session_state or st.session_state.matches is None:
    # Refresh matches data
    get_session_matches()
    st.rerun()


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
title_col, refresh_col, new_col = st.columns([16,2,3])
with title_col:
    st.title("Mes matchs")
with refresh_col:
    st.space("small")
    if st.button("🔄 Refresh"):
        # Remove matches from the session to rescan them
        del st.session_state["matches"]
        st.rerun()  
    st.space("small")    
with new_col:
    st.space("small")
    if st.button("➕ Nouveau match"):
        creation_hash = {
            "name": "Nouveau match",
            "board": json.dumps(TEMPLATE_SCORE_BOARD),
            "editor": [st.session_state["token"]], 
            "viewers": [st.session_state["token"]]
        }
        upsert_match("create", match_hash=creation_hash)
    st.space("small")

# List matches linked to the user
cmpt = 0
for match in st.session_state.matches[:st.session_state.displayed_matches]:
    cmpt += 1
    with st.container():
        l, r, rr = st.columns([6,2,1])
        with l:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1em; margin-right: 10px;">
                        {'✏️' if st.session_state.token in match.get('editor') else '👁️'}
                    </span>
                    <h3 style='text-align: left; color: #FFA139; margin: 0;'>
                        {match.get('name', '')}
                    </h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            date_col, score_col = st.columns(2)
            with date_col:
                st.write(f"#### Date: {match.get('date')}")
            with score_col:
                st.write(f"#### Score : {match.get('display_score', '-')}")
        with r:
            if st.button(f"Ouvrir ce match", key=f"recap_{match.get('match_id')}"):
                open_match(match.get("match_id"))
        with rr:
            if st.button(f"🗑️", key=f"delete_{match.get('match_id')}", type="primary"):
                if st.session_state.token in match.get("editor"):
                    # Delete match if the user is the editor
                    if match.get("video"):
                        delete_video_from_gcs(match.get("video"))
                    upsert_match("delete", match_id=match.get("match_id"))
                else:
                    # Remove user from viewers else
                    new_viewers = [usr_hash.get("token") for usr_hash in json.loads(match.get("viewers_footprint")) if usr_hash.get("token") != st.session_state.token]
                    upsert_match("update", match_id=match.get("match_id"), match_hash={"viewers": new_viewers})
                # Remove matches from the session to rescan them
                del st.session_state["matches"]
                st.rerun()
        if cmpt == st.session_state.displayed_matches:
            if len(st.session_state.matches) > st.session_state.displayed_matches:
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

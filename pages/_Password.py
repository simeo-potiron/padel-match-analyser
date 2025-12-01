# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
import time

# Streamlit Package
import streamlit as st

# Datetime Packages
from datetime import datetime, timedelta


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
st.set_page_config(page_title="Password", layout="centered")


# ~~~~    Initial checks    ~~~~ #
# Reset session state
for key in st.session_state:
    del st.session_state[key]


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
st.title("Réinitialisation du mot de passe")

# Reset password fields
utms = st.query_params
if "token" not in utms.keys():
    st.switch_page("Home.py")
else:
    # Check if reset_link is still valid
    if check_reset_link_valid(utms["token"]):
        # Save new password
        new_mdp_1 = st.text_input("Nouveau mot de passe:", type="password")
        new_mdp_2 = st.text_input("Confirmer nouveau mot de passe:", type="password")
        if st.button("Réinitialiser") or (new_mdp_1 and new_mdp_2):
            if len(new_mdp_1 or "") >= 4 and new_mdp_1 == new_mdp_2:
                user_updated = upsert_user("update", token=utms["token"], user_hash={"password": new_mdp_1, "reset_link_expiration_time": None})
                st.success("Votre mot de passe a bien été mis à jour")
                time.sleep(2)
                st.switch_page("pages/_LogIn.py")
            elif len(new_mdp_1 or "") < 4:
                st.error("Le mot de passe doit comporter quatre caractères ou plus")
            else:
                st.error("Les mots de passe renseignés doivent être identiques")
    else:
        st.error("Le lien de réinitialisation a expiré")
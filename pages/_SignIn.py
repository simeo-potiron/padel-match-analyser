# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
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
st.set_page_config(page_title="SignIn", layout="centered")


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
st.title("Création d'un compte")

# Authentification fields
email = st.text_input("Email")
mdp_1 = st.text_input("Mot de passe", type="password")
mdp_2 = st.text_input("Confirmer mot de passe", type="password")

# Bottom buttons
if st.button("Inscription") or (mdp_1 and mdp_2):
    if len(mdp_1 or "") >= 4 and (mdp_1 == mdp_2):
        signed_in = signin(email, mdp_1)
        if signed_in:
            st.success("Connexion au compte en cours...")
            time.sleep(2)
            st.switch_page("Home.py")
        else:
            st.error("Cet email est déjà utilisé par un autre utilisateur")
            time.sleep(2)
            st.switch_page("pages/_LogIn.py")
    elif len(mdp_1 or "") < 4:
        st.error("Le mot de passe doit comporter quatre caractères ou plus")
    else:
        st.error("Les mots de passe renseignés doivent être identiques")

# Link to the Log In page if they already have an account
st.page_link("pages/_LogIn.py", label="Tu as déjà un compte ? Connecte toi ici !", icon="📝")

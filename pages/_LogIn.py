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
st.set_page_config(page_title="LogIn", page_icon="🎾", layout="centered")


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


# ~~~~    Pop-Up functions    ~~~~ #
# Pop-Up: Reset password
@st.dialog("Réinitialiser votre mot de passe", width="small", dismissible=True, on_dismiss="rerun")
def reset_password(previous_email):
    email_to_reset = st.text_input("Renseigner votre email ici:", value=previous_email or "")
    if st.button("Réinitialiser"):
        reset_link = generate_reset_link(email_to_reset)
        if reset_link is not None:
            email_sent = send_email(
                to_email="simeo.potiron@laposte.net", 
                type="reset_password",
                reset_link=reset_link
            )
            if email_sent:
                expiration_time = datetime.now() + timedelta(minutes=60)
                upsert_user("update", token=user_token, user_hash={"reset_link_expiration_time": expiration_time.strftime("%Y-%m-%d %H:%M:%S")})
                st.success("Un mail de réinitialisation vous a été envoyé")
            else:
                st.error("Le mail de réinitialisation n'a pas pu être envoyé, veuillez réessayer ultérieurement")
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"Cet email ne correspond à aucun utilisateur")
            time.sleep(2)
            st.rerun()


# ~~~~    Page core    ~~~~ #
# Header
st.title("Connexion à un compte")

# Authentification fields
email = st.text_input("Email")
mdp = st.text_input("Mot de passe", type="password")

# Bottom buttons
with st.container(horizontal=True):
    # Reset password
    if st.button("Mot de passe oublié ?", type="tertiary"):
        reset_password(email)

    # Login
    if st.button("Connexion") or (email and mdp):
        logged_in = login(email, mdp)
        if logged_in:
            st.success("Connexion au compte en cours...")
            time.sleep(2)
            st.switch_page("Home.py")
        else:
            st.error("Identifiants incorrects")
            time.sleep(2)
            st.rerun()

# Redirection to Sign In page for new users
st.page_link("pages/_SignIn.py", label="Nouveau ? Inscris-toi ici !", icon="📝")
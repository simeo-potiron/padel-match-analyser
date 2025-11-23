import streamlit as st
import time
from datetime import datetime, timedelta

from utils import *

st.set_page_config(page_title="LogIn", page_icon="🎾", layout="centered")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Connexion à un compte")

if "processing" not in st.session_state:
    st.session_state.processing = False

email = st.text_input("Email", disabled=st.session_state.processing)
mdp = st.text_input("Mot de passe", type="password", disabled=st.session_state.processing)

with st.container(horizontal=True):
    # Reset password
    @st.dialog("Réinitialiser votre mot de passe", width="small", dismissible=True, on_dismiss="rerun")
    def reset_password(previous_email):
        email_to_reset = st.text_input("Renseigner votre email ici:", value=previous_email or "")
        if st.button("Réinitialiser", disabled=st.session_state.processing):
            st.session_state.processing = True
            user = check_email(email_to_reset)
            if user:
                user_token = user.get("id")
                BASE_URL, RESET_PAGE = st.secrets["app"]["base_url"], "Password"
                reset_link = f"{BASE_URL}/{RESET_PAGE}?token={user_token}"
                rep = send_email(
                    to_email="simeo.potiron@laposte.net", 
                    type="reset_password",
                    reset_link=reset_link
                )
                if rep["status"] == "success":
                    expiration_time = datetime.now() + timedelta(minutes=60)
                    update_user(user_token, {"reset_link_expiration_time": expiration_time.strftime("%Y-%m-%d %H:%M:%S")})
                    st.success("Un mail de réinitialisation vous a été envoyé")
                elif rep["status"] == "failure":
                    st.error("Le mail de réinitialisation n'a pas pu être envoyé")
                time.sleep(2)
                st.session_state.processing = False
                st.rerun()
            else:
                st.error(f"Cet email ne correspond à aucun utilisateur")
                time.sleep(2)
                st.session_state.processing = False
                st.rerun()

    if st.button("Mot de passe oublié ?", type="tertiary"):
        reset_password(email)

    # Login
    if st.button("Connexion", disabled=st.session_state.processing) or (email and mdp):
        st.session_state.processing = True
        auth = login(email, mdp)
        if auth:
            st.session_state.token = auth["token"]
            st.success("Connexion réussie !")
            time.sleep(2)
            st.session_state.processing = False
            st.switch_page("Home.py")
        else:
            st.error("Identifiants incorrects")
            time.sleep(2)
            st.session_state.processing = False
            st.rerun()

# Lien vers le Sign In
st.page_link("pages/_SignIn.py", label="Nouveau ? Inscris-toi ici !", icon="📝")
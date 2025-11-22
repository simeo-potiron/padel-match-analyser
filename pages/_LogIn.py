import streamlit as st
from utils import login, send_email

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

username = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")

with st.container(horizontal=True):
    # Reset password
    if st.button("Mot de passe oublié ?", type="tertiary"):
        rep = send_email(
            to_email="simeo.potiron@laposte.net", 
            type="reset_password"
        )
        if rep["status"] == "success":
            st.success(rep["message"])
        elif rep["status"] == "failure":
            st.error(rep["message"])
        else:
            st.error("Failed to send email")


    # Login
    if st.button("Connexion") or password:
        auth = login(username, password)

        if auth:
            st.session_state.token = auth["token"]
            st.success("Connexion réussie !")
            st.switch_page("Home.py")
        else:
            st.error("Identifiants incorrects")

# Lien vers le Sign In
st.page_link("pages/_SignIn.py", label="Nouveau ? Inscris-toi ici !", icon="📝")
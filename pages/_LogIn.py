import streamlit as st
from utils import login

st.set_page_config(page_title="LogIn", page_icon="🎾", layout="centered")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Connexion à un compte existant")

username = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")

if st.button("Connexion") or password:
    auth = login(username, password)

    if auth:
        st.session_state["token"] = auth["token"]
        st.success("Connexion réussie !")
        st.switch_page("Home.py")
    else:
        st.error("Identifiants incorrects")

# Lien vers le Sign In
st.page_link("pages/_SignIn.py", label="Nouveau ? Inscris-toi ici !", icon="📝")

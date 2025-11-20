import streamlit as st
from utils import signin

st.set_page_config(page_title="SignIn", layout="centered")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Création d'un nouveau compte")

username = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")

if st.button("Inscription") or password:
    auth = signin(username, password)

# Lien vers le LogIn
st.page_link("pages/_LogIn.py", label="Tu as déjà un compte ? Connecte toi ici !", icon="📝")

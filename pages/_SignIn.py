import streamlit as st

from utils import *

st.set_page_config(page_title="SignIn", layout="centered")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Création d'un compte")

email = st.text_input("Email")
mdp_1 = st.text_input("Mot de passe", type="password")
mdp_2 = st.text_input("Confirmer mot de passe", type="password")

if st.button("Inscription") or (mdp_1 and mdp_2):
    if len(mdp_1 or "") >= 4 and (mdp_1 == mdp_2):
        auth = signin(email, mdp_1)
        if auth and "token" in auth.keys():
            st.success("Votre compte a bien été créé")
            st.session_state.token = auth["token"]
            time.sleep(2)
            st.switch_page("Home.py")
        elif auth and "token" not in auth.keys():
            st.error(auth.message)
        else:
            st.error("Une erreur inconnue est apparue pendant de la création de votre compte")
    elif len(mdp_1 or "") < 4:
        st.error("Le mot de passe doit comporter quatre caractères ou plus")
    else:
        st.error("Les mots de passe renseignés doivent être identiques")

# Lien vers le LogIn
st.page_link("pages/_LogIn.py", label="Tu as déjà un compte ? Connecte toi ici !", icon="📝")

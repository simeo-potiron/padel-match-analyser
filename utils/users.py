# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages


# Datetime Packages
from datetime import datetime, timedelta

# Streamlit Package
import streamlit as st

# Airtable Package
from pyairtable import Api

# Bcrypt Package
import bcrypt


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import UTILS FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from .utils import send_email


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import GLOBAL VARIABLES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from storage import *


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Authenticate Airtable API    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

AT_API = Api(AT_TOKEN)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def require_login():
    """
    Checks that the session is authentified and redirect to Login page otherwise
    """
    # Rediriger vers la page de login si le token est vide (<=> pas de user actif)
    if ("token" not in st.session_state) or (st.session_state.token is None):
        st.switch_page("pages/_LogIn.py")

def hash_password(password):
    """
    Hash a password with salt & pepper using Bcrypt
    """
    # Concaténer le mot de passe clair et le pepper
    password_with_pepper = password.encode("utf-8") + PASSWORD_PEPPER.encode("utf-8")
    # Hacher le résultat (bcrypt ajoute son propre sel)
    hashed_bytes = bcrypt.hashpw(password_with_pepper, bcrypt.gensalt(rounds=12))
    return hashed_bytes.decode('utf-8')

def check_password(password, hashed_password):
    """
    Check if the provided password matches the hashed password
    """
    # Concaténer le mot de passe clair et le pepper
    password_with_pepper = password.encode("utf-8") + PASSWORD_PEPPER.encode("utf-8")
    # Vérifier le hachage
    return bcrypt.checkpw(password_with_pepper, hashed_password.encode('utf-8'))

def check_email(email, password=None):
    """
    Check if an email is used or not and if it's linked to the requested password.
    Return a response code depending on the situation:
        - "-1": The email exists but the password is wrong
        - "0": The email does not exist
        - "1": The email exists (and match the password if provided)
    """
    # Connexion à Airtable
    users_table = AT_API.table(PADEL_BASE_ID, USERS_TABLE_ID)
    
    # Récupération des records correspondant à l'email
    email = email.lower()
    formula = f"{{email}} = '{email}'"
    user = users_table.first(formula=formula)
    if user:
        if password:
            if check_password(password, user.get("fields").get("password_h")):
                resp_hash = {
                    "resp_code": 1, 
                    "message": "Cet email est bien celui d'un utilisateur actif", 
                    "token": user.get("id"),
                    "user": {key: val for key, val in user.get("fields").items() if key in USER_SESSION_STATE_FIELDS}
                }
            else:
                resp_hash = {
                    "resp_code": -1, 
                    "message": "Email/Password invalide",
                    "token": None,
                    "user": None
                }
        else:
            resp_hash = {
                "resp_code": 1, 
                "message": "Cet email est bien celui d'un utilisateur actif",
                "token": user.get("id"),
                "user": None
            }
    else:
        resp_hash = {
            "resp_code": 0, 
            "message": "Cet email ne correspond à aucun utilisateur",
            "token": None,
            "user": None
        }

    return resp_hash

def login(email, password):
    """
    Try to log in using provided email and password
    """
    # Vérifie si l'email et le password correspondent à un user actif
    resp = check_email(email, password=password)

    # Mettre à jour la session
    st.session_state.token = resp.get("token")
    st.session_state.user = resp.get("user")
    
    return st.session_state.token is not None

def signin(email, password):
    """
    Try to log in if the provided email match a user, else create a new user using the provided password
    """
    # Vérifie si un user avec ce mail existe déjà
    resp = check_email(email, password=password)
    if resp["resp_code"] == 0:
        # S'il n'existe pas, le créer
        new_user_hash = {
            "email": email,
            "password_h": hash_password(password)
        }
        upsert_user("create", user_hash=new_user_hash)
    else:
        # Mettre à jour la session
        st.session_state.token = resp.get("token")
        st.session_state.user = resp.get("user")

    return st.session_state.token is not None

def generate_reset_link(email):
    """
    Generate a reset_link to allow a user to reset his password
    """
    # Vérifier si un user avec ce mail existe bien
    resp = check_email(email)

    # Générer le reset_link
    if resp["resp_code"] == 1:
        return f"{BASE_URL}/Password?token={resp['token']}"
    else:
        return None

def check_reset_link_valid(token):
    """
    Checks if the reset link is expired
    """
    # Connexion à Airtable
    users_table = AT_API.table(PADEL_BASE_ID, USERS_TABLE_ID)
    
    # Vérification de la date limite liée au reset link
    user = users_table.get(token)
    expiration_time = user.get("fields").get("reset_link_expiration_time")
    
    return expiration_time and (datetime.strptime(expiration_time, "%Y-%m-%dT%H:%M:%S.%fZ") >= datetime.now())

def upsert_user(type, token=None, user_hash=None):
    """
    Upsert a user in airtable:
        - Store new user
        - Update stored user with latest changes
        - Delete user
    """
    # Connexion à Airtable
    users_table = AT_API.table(PADEL_BASE_ID, USERS_TABLE_ID)

    if type == "create" and user_hash:
        # Créer le record
        new_user = users_table.create(user_hash)
        st.session_state.token = new_user.get("id")
        st.session_state.user = {key: val for key, val in new_user.get("fields").items() if key in USER_SESSION_STATE_FIELDS}
    
    elif type == "update" and token and user_hash:
        # Mettre à jour le record
        updated_user = users_table.update(token, user_hash)
        st.session_state.token = updated_user.get("id")
        st.session_state.user = {key: val for key, val in updated_user.get("fields").items() if key in USER_SESSION_STATE_FIELDS}

    # elif type == "delete" and token:
    #     # Mettre à jour le record
    #     users_table.delete(token)
    #     st.session_state.token = None
    #     st.session_state.user = None

    return st.session_state.token is not None

def get_other_users(tokens):
    """
    Retrieve id and email of all users (not having their id stored in tokens)
    """
    # Connexion à Airtable
    users_table = AT_API.table(PADEL_BASE_ID, USERS_TABLE_ID)

    # Récupération des infos des utilisateurs
    all_users = users_table.all()
    other_users = [{ "token":usr.get("id"), "email":usr.get("fields").get("email") } for usr in all_users if usr.get("id") not in tokens]

    return other_users
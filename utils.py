import streamlit as st
import pyairtable as at
from google.cloud import storage
import tempfile
import uuid

# -----------------------------------------------------
# CONFIGURATION Airtable
# -----------------------------------------------------
AT_TOKEN = "pat4ky59ivDvVqBku.0a1ed02ff3983c1b10cd3e6284789c58ad363eb60bf2e144585518bd7e4f98bd"
AT_TABLES = {
    "Users": {
        "base": "appHpJoih6uBVyjyC",
        "table": "tblHyMeKRpnvgx6mb"
    },
    "Matchs": {
        "base": "appHpJoih6uBVyjyC",
        "table": "tblxB67Tdd0S2Yl5s"
    }
}

# -----------------------------------------------------
# CONFIGURATION GCS
# -----------------------------------------------------
BUCKET_NAME = "padel-matchs"

# -----------------------------------------------------
# FUNCTIONS Login
# -----------------------------------------------------
def require_login():
    if "token" not in st.session_state:
        st.switch_page("pages/_LogIn.py")

def login(email, password):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])
    
    # Récupération des records correspondant 
    formula = f"AND( {{email}} = '{email}', {{password}} = '{password}' )"
    user = table.first(formula=formula)

    # Validation de l'accès si un record a été trouvé
    if user:
        return {"token": user.get("id")}
    else:
        return None

def signin(email, password):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])
    
    # Récupération des records correspondant à l'email
    formula = f"{{email}} = '{email}'"
    user = table.first(formula=formula)

    # Check si le user existe déjà
    if user:
        if password == user.get("fields").get("password"):
            return {"token": user.get("id")}
        else:
            return {"message": "Cet email est déjà utilisé"}
    else:
        # S'il n'existe pas, le créer
        new_user_hash = {
            "email": email,
            "password": password
        }
        new_user = table.create(new_user_hash)
        return {"token": new_user.get("id")}

def update_password(token, password):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])

    # Mise à jour du record
    updated_user = table.update(token, {"password": password})
    return {"token": updated_user.get("id")}

# -----------------------------------------------------
# FUNCTIONS Matches
# -----------------------------------------------------
def get_matches(token):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Matchs"]["base"], AT_TABLES["Matchs"]["table"])

    # Connexion au record
    formula = f"{{user}} = '{token}'"
    return table.all(formula=formula)

def upsert_match(type, match_id="", match_hash={}):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Matchs"]["base"], AT_TABLES["Matchs"]["table"])

    if type == "create" and match_hash:
        return table.create(match_hash)
    elif type == "update" and match_id and match_hash:
        return table.update(match_id, match_hash)
    elif type == "delete" and match_id:
        return table.delete(match_id)
    else:
        return None

def get_match_data(match_id, field):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Matchs"]["base"], AT_TABLES["Matchs"]["table"])
    match = table.get(match_id)
    return match.get("fields").get(field)

# -----------------------------------------------------
# FUNCTIONS Videos
# -----------------------------------------------------
# from gcs-key import 

# # Les stocker temporairement
# with tempfile.NamedTemporaryFile(delete=False) as tmp:
#     tmp.write(json.dumps(creds).encode("utf-8"))
#     cred_path = tmp.name

def store_video_to_gcs(file):
    cred_path = "gcs-key.json"
    destination_blob_name = f"{uuid.uuid4()}.mp4"
    client = storage.Client.from_service_account_json(cred_path)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file, content_type=file.type)
    blob.make_public()
    return blob.public_url

def delete_video_from_gcs(video_url):
    cred_path = "gcs-key.json"
    destination_blob_name = video_url.split("/")[-1]
    client = storage.Client.from_service_account_json(cred_path)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.delete()
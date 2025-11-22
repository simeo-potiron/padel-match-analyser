import streamlit as st
import pyairtable as at
from google.cloud import storage
import tempfile
import uuid
import smtplib
from email.message import EmailMessage

# -----------------------------------------------------
# CONFIGURATION Airtable
# -----------------------------------------------------
AT_TOKEN = st.secrets["airtable"]["token"]
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
GCS_INFO = st.secrets["google-service-account"]
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
    email = email.lower()
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
    email = email.lower()
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

def send_email(to_email, type):
    # Retrieve SMTP elements from streamlit secrets
    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = st.secrets["email"]["smtp_port"]
    sender_email = st.secrets["email"]["sender_email"]
    app_password = st.secrets["email"]["app_password"]
    
    # Prepare email content and topic
    sender = "Padel match analyser"
    if type == "reset_password":
        topic = "Reset your password"
        content = "Clic on this link and reset your password"
    else:
        topic, content = None, None

    # Create a text/plain message
    if topic and content and to_email:
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = topic
        msg['From'] = sender
        msg['To'] = to_email


        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            smtp.quit()

        return {"status": "success", "message": "Email sent successfully"}
    
    else:
        return {"status": "failure", "message": "Missing some arguments"}

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
def store_video_to_gcs(file):
    destination_blob_name = f"{uuid.uuid4()}.mp4"
    client = storage.Client.from_service_account_info(GCS_INFO)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file, content_type=file.type)
    blob.make_public()
    return blob.public_url

def delete_video_from_gcs(video_url):
    destination_blob_name = video_url.split("/")[-1]
    client = storage.Client.from_service_account_info(GCS_INFO)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.delete()
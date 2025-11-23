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

def check_email(email):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])
    
    # Récupération des records correspondant à l'email
    email = email.lower()
    formula = f"{{email}} = '{email}'"
    return table.first(formula=formula)

def signin(email, password):
    # Check si le user existe déjà
    user = check_email(email)
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

def update_user(token, user_hash):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])

    # Mise à jour du record
    updated_user = table.update(token, user_hash)
    return {"token": updated_user.get("id")}

def send_email(to_email, type, reset_link=None):
    # Retrieve SMTP elements from streamlit secrets
    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = st.secrets["email"]["smtp_port"]
    sender_email = st.secrets["email"]["sender_email"]
    app_password = st.secrets["email"]["app_password"]
    
    # Prepare email content and topic
    sender = "Padel match analyser <simeopot@gmail.com>"
    if type == "reset_password" and reset_link:
        topic = "Réinitialisez votre mot de passe"
        content = f"Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_link}"
        html_content = f"""\
        <html>
        <body>
            <p>Bonjour,</p>
            <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
            <p>Cliquez sur le lien ci-dessous pour continuer. Ce lien expirera dans 60 minutes :</p>
            <a href="{reset_link}">Réinitialiser mon mot de passe</a>
            <p>Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet e-mail.</p>
        </body>
        </html>
        """
    else:
        topic, content, html_content = None, None

    # Create a text/plain message and send it
    if topic and content and to_email:
        # Prepare email
        msg = EmailMessage()
        msg.set_content(content)
        if html_content:
            msg.add_alternative(html_content, subtype='html')
        msg['Subject'] = topic
        msg['From'] = sender
        msg['To'] = to_email
        # Send email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            smtp.quit()
        return {"status": "success"}
    else:
        return {"status": "failure"}

def get_user_infos(token):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])
    user = table.get(token)

    return user.get("fields")

def get_other_users(tokens):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Users"]["base"], AT_TABLES["Users"]["table"])
    all_users = table.all()
    return [usr for usr in all_users if usr.get("id") not in tokens]

# -----------------------------------------------------
# FUNCTIONS Matches
# -----------------------------------------------------
def get_matches(token):
    # Get matchs linked to this user
    match_ids = get_user_infos(token).get("matchs")

    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Matchs"]["base"], AT_TABLES["Matchs"]["table"])
    formula = f"FIND(RECORD_ID(), '{', '.join(match_ids)}') > 0"

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

def get_match_data(match_id):
    # Connexion à Airtable
    table = at.Table(AT_TOKEN, AT_TABLES["Matchs"]["base"], AT_TABLES["Matchs"]["table"])
    match = table.get(match_id)
    return match.get("fields")

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

# -----------------------------------------------------
# FUNCTIONS Utils
# -----------------------------------------------------
def compare_objects(obj_1, obj_2):
    # Check they are the same type of objects
    if type(obj_1) != type(obj_2):
        return False
    
    # Compare objects depending on their types
    match type(obj_1):
        case dict():
            # Compare dicts
            for key in obj_1.keys:
                if not compare_objects(obj_1.get(key), obj_2.get(key)):
                    return False
            return True
        case list():
            # Compare lists of objects
            if len(obj_1) == len(obj_2):
                for el_1 in obj_1:
                    found = False
                    for el_2 in obj_2:
                        if compare_objects(el_1, el_2):
                            found = True
                            break
                    if not found:
                        return False
                return True
            else:
                return False
        case _:
            try:
                return obj_1 == obj_2
            except:
                return False
                
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages


# SMTP Packages
import smtplib
from email.message import EmailMessage


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import GLOBAL VARIABLES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from storage import *


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def send_email(to_email, type, reset_link=None):
    """
    Send an email to a specified adress using SMTP server
    """  
    # Prepare email content and topic
    sender = f"Padel match analyser <{SMTP_SENDER_EMAIL}>"
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
        topic, content, html_content = None, None, None

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
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SMTP_SENDER_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
            smtp.quit()
        return {"status": "success"}
    else:
        return {"status": "failure"}

def compare_objects(obj_1, obj_2):
    """
    Compare 2 objects (dict, list, str, int, etc...) and return if they are basically the same
    """
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

def union_lists(list_1, list_2):
    """
    Return the union of two lists
    """
    # Si l'une des listes est vide, il suffit de concatener
    if list_1 and list_2:
        # On s'assure d'ajouter la plus petite à la plus grande
        if len(list_1) > len(list_2):
            list_a, list_b = list_1, list_2
        else:
            list_a, list_b = list_2, list_1
        return list_a + [el for el in list_b if not el in list_a]
    else:
        return (list_1 or []) + (list_2 or [])

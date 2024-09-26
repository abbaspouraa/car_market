import os
import base64
import pickle
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


def get_service():
    client_secret_file = 'email_script/client_secret.json'
    api_name = 'gmail'
    api_version = 'v1'
    scopes = ['https://mail.google.com/']

    cred = None

    pickle_file = f'Token_{api_name}_{api_version}.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_name, api_version, credentials=cred)
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def send_email(email_address, message, subject):
    service = get_service()

    mime_message = MIMEMultipart()
    mime_message['to'] = email_address
    mime_message['subject'] = subject
    mime_message.attach(MIMEText(message, "html"))
    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")

    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()

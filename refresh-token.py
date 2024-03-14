#!/usr/bin/env python

import pickle
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_refresh_token():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server()
    return creds.refresh_token

def get_credentials(refresh_token, client_id, client_secret):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    # Check if token is expired and refresh if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds

# Load credentials from credentials.json
with open('credentials.json', 'r') as credentials_file:
    creds_data = json.load(credentials_file)
    client_id = creds_data['installed']['client_id']
    client_secret = creds_data['installed']['client_secret']

# Get refresh token
refresh_token = get_refresh_token()

# Get credentials using the refresh token
creds = get_credentials(refresh_token, client_id, client_secret)

# Save the credentials along with client ID and client secret to token.pickle
credentials_info = {
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token
}

with open('token.pickle', 'wb') as token_file:
    pickle.dump(credentials_info, token_file)

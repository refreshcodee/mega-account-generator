#!/usr/bin/env python

import re
import json
import faker
import random
import string
import subprocess
import time
import argparse
import pickle
from base64 import urlsafe_b64decode
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.utils import parseaddr

MEGATOOLS = r"E:\megatools-1.11.1.20230212-win64\megatools.exe"
MAIL = "abc"

email_data = {}

def load_credentials():
    try:
        with open('token.pickle', 'rb') as token_file:
            credentials_info = pickle.load(token_file)
            client_id = credentials_info['client_id']
            client_secret = credentials_info['client_secret']
            refresh_token = credentials_info['refresh_token']
            creds = Credentials(
                None,  # No access token
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret
            )

            # Refresh the token if it's expired
            if creds.expired and creds.refresh_token:
                return "Rerun refresh-token.py file."
                
            return creds
    except FileNotFoundError:
        return None

def generate_fake_email():
    global email_data
    fake = faker.Faker()

    real_name = fake.name()
    random_thing = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 10)))
    email = f"{MAIL}+{random_thing}@gmail.com"
    password = fake.password()
        
    email_data = {
        "real_name": real_name,
        "email": email,
        "password": password
    }
    
    return json.dumps(email_data, indent=4)

def register_mega(name, email, password):
    register_command = subprocess.run(fr'{MEGATOOLS} reg --scripted --register --email "{email}" --name "{name}" --password "{password}"', shell=True, capture_output=True, text=True).stdout
    return register_command
    
def verify_mega(register, link):
    verify_command = register.replace("megatools", MEGATOOLS).replace("@LINK@", link)
    subprocess.run(verify_command, shell=True, capture_output=True, text=True).stdout
    return json.dumps({
        "email": email_data.get('email'),
        "password": email_data.get('password'),
        "real_name": email_data.get('real_name')
    })

def check_email(creds, email):
    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Define the recipient email address
    recipient_email = email

    # List to store email details
    emails = []

    # Get messages from the inbox label
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=f"to:{recipient_email}").execute()
    messages = results.get('messages', [])

    # Iterate over each message and get its content
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers = msg['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        if subject and "MEGA email verification required" in subject:
            payload = msg['payload']
            if 'parts' in payload:
                parts = payload['parts']
                body = None
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body']['data']
                        body = urlsafe_b64decode(body_data).decode()
                        break
            else:
                body_data = payload['body']['data']
                body = urlsafe_b64decode(body_data).decode()
            
            if body:
                urls = re.findall(r'(https?://\S+)', body)
                for url in urls:
                    if 'mega.nz' in url:
                        email_details = {
                            "subject": subject,
                            "from": parseaddr(next(header['value'] for header in headers if header['name'] == 'From'))[1],
                            "to": parseaddr(next(header['value'] for header in headers if header['name'] == 'To'))[1],
                            "date": next(header['value'] for header in headers if header['name'] == 'Date'),
                            "url": url
                        }
                        emails.append(email_details)
                        
    if len(emails) == 0:
        return "Nothing found"
    return emails
    
def store_email_data(email_id, password):
    with open('accounts.txt', 'a') as txtfile:
        txtfile.write(f"{email_id}:{password}\n")

def generate_mega_accounts(num):
    
    creds = load_credentials()
    if creds is None:
        print("Credentials not found or expired, run refresh-token.py file.")
        
    for i in range(num):
        generate_fake_email() # Generate mails and password
        
        name = email_data.get('real_name')
        email_id = email_data.get('email')
        password = email_data.get('password')

        register = register_mega(name, email_id, password) # Register Mega account

        time.sleep(10) # Waiting for mail to arrive

        verification_mail = check_email(creds ,email_data.get('email')) # Get Verification mail
        account = verify_mega(register, verification_mail[0].get('url')) # Verify Mega account

        store_email_data(email_id, password) # Add account to json file

        print(account)
        
        email_data.clear() # Clear the dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Mega Accounts")
    parser.add_argument("--n", type=int, default=1, help="The number of mega accounts to generate")
    args = parser.parse_args()
    
    generate_mega_accounts(args.n)

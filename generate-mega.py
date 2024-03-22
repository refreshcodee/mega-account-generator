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
import requests
import logging
from base64 import urlsafe_b64decode
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.utils import parseaddr
from datetime import datetime, timezone

MEGATOOLS = r"E:\megatools-1.11.1.20230212-win64\megatools.exe"
MAIL = "youremailbefore@sign"

email_data = {}

log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_mega.log'
logging.basicConfig(filename=f"E:\upload-bot\logs\{log_filename}", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load credentials
def load_credentials():
    try:
        logging.info("Loading Credentials")
        with open('E:\upload-bot\token.pickle', 'rb') as token_file:
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
            logging.info("Credentials Loaded")

            # Refresh the token if it's expired
            if creds.expired and creds.refresh_token:
                logging.error("Credentials expired")
                return "Rerun refresh-token.py file."
                
            return creds
    except FileNotFoundError:
        error_message = "File 'token.pickle' not found."
        logging.error(error_message)
        return

# Function to generate fake email
def generate_fake_email():
    global email_data
    try:
        logging.info("Generating Fake Email")
        fake = faker.Faker()
        real_name = fake.name()
        random_thing = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 10)))
        email = f"{MAIL}+{random_thing}@gmail.com"  # Assuming MAIL is defined somewhere
        password = fake.password()

        email_data = {
            "real_name": real_name,
            "email": email,
            "password": password
        }
        logging.info("Generated Fake Email Successfully")
        logging.info(email_data)
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logging.error(error_message)
        return

# Function to register on Mega
def register_mega(name, email, password):
    try:
        logging.info("Registering on MEGA")
        register_command = subprocess.run(fr'{MEGATOOLS} reg --scripted --register --email "{email}" --name "{name}" --password "{password}"', shell=True, capture_output=True, text=True)
        logging.info(register_command)
        register_output = register_command.stdout
        register_error = register_command.stderr
        if register_error:
            logging.error("Couldn't Register MEGA Account")
            raise ValueError(register_error)
        logging.info("Registered MEGA Account Successfully")
        return register_output
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logging.error(error_message)
        return

# Function to verify Mega registration
def verify_mega(register, link):
    try:
        logging.info("Verifying MEGA Account")
        verify_replace_link = register.replace("megatools", MEGATOOLS).replace("@LINK@", link)
        logging.info(verify_replace_link)
        verify_command = subprocess.run(verify_replace_link, shell=True, capture_output=True, text=True)
        verify_output = verify_command.stdout
        verify_error = verify_command.stderr
        if verify_error:
            logging.error("Couldn't verify MEGA Account")
            raise ValueError(verify_error)
        logging.info(verify_output)
        return json.dumps({
            "email": email_data.get('email'),
            "password": email_data.get('password'),
            "real_name": email_data.get('real_name')
        })
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logging.error(error_message)
        return

# Function to check email
def check_email(creds, email):
    try:
        logging.info("Checking Email for Verification Link")
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Define the recipient email address
        recipient_email = email

        # List to store email details
        emails = []

        # Get messages from the inbox label
        logging.info("Getting Emails")
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
        return emails
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logging.error(error_message)
        return
    
# Function to store email data
def store_email_data(email_id, password):
    try:
        logging.info("Storing MEGA Account to accounts.txt")
        with open('E:\upload-bot\accounts.txt', 'a') as txtfile:
            txtfile.write(f"{email_id}:{password}\n")
        logging.info("Added MEGA Account to accounts.txt")
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logging.error(error_message)

# Function to generate Mega accounts
def generate_mega_accounts(num):
    try:
        creds = load_credentials()
        if creds is None:
            raise Exception("Credentials not found or expired, run refresh-token.py file.")
        
        start_time = time.time()
        
        for i in range(num):
            generate_fake_email() # Generate mails and password
            
            name = email_data.get('real_name')
            email_id = email_data.get('email')
            password = email_data.get('password')

            register = register_mega(name, email_id, password) # Register Mega account

            verification_mail = None
            
            while True:
                verification_mail = check_email(creds ,email_data.get('email')) # Get Verification mail
                if (len(verification_mail) != 0):
                    break
                if time.time() - start_time >= 600:
                    raise ValueError("Timeout: 10 minutes elapsed. Exiting loop.")
                time.sleep(10)
                
            account = verify_mega(register, verification_mail[0].get('url')) # Verify Mega account

            store_email_data(email_id, password) # Add account to json file

            print(account)
            
            email_data.clear() # Clear the dict
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        logging.error(error_message)
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Mega Accounts")
    parser.add_argument("--n", type=int, default=1, help="The number of mega accounts to generate")
    args = parser.parse_args()
    
    generate_mega_accounts(args.n)

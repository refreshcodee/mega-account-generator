# mega-account-generator

mega-account-generator is a tool used to generate Mega accounts using Gmail and Megatools.

## Requirements

- Python 3.11.0
- Megatools: [Download Megatools](https://megatools.megous.com/)

## How to Install

```bash
pip install -r requirements.txt
```

## Configure Gmail API

To use Gmail API, you need to configure it in the Google Cloud console. Follow the steps below:

1. Go to [Set up your environment](https://developers.google.com/gmail/api/quickstart/python) and follow all the instructions.
2. Make sure to select User type as External in [OAuth consent screen](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen) and grant all Gmail Scopes.
3. Follow the instructions to complete the setup.
4. Save the downloaded JSON file as credentials.json, and move the file to your working directory.

## Scripts

- `generate-mega.py`: Generates Mega accounts.
- `signin_accounts.py`: Keeps Mega accounts alive (Thanks to [f-o/MEGA-Account-Generator](https://github.com/f-o/MEGA-Account-Generator)).
- `refresh-token.py`: Generates `token.pickle` used for Gmail authentication.

## How to Use

1. Replace the `MEGATOOLS` variable in `generate-mega.py` with your Megatools path.
2. Replace the `MAIL` variable in `generate-mega.py` with your gmail username.
3. Run `python refresh-token.py` to generate `token.pickle` (Run only once and make sure to run on local machine rather than a server).
4. Copy `token.pickle` to your working folder (Only needed if you plan to run the script on a server, otherwise ignore as it creates the file in the working directory itself).
5. Run `python generate-mega.py`.

### Demo

```bash
python generate-mega.py --help
usage: generate-mega.py [-h] [--n N]

Generate Mega Accounts

options:
  -h, --help  show this help message and exit
  --n N       The number of mega accounts to generate
```

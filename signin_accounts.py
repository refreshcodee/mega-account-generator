#!/usr/bin/env python

import json
import subprocess

def main():
    MEGATOOLS = r"E:\megatools-1.11.1.20230212-win64\megatools.exe"
    with open('accounts.json', 'r') as file:
        # Load the contents of the file into a Python object
        accounts = json.load(file)

        for account in accounts:
            email = account.get('email')
            password = account.get('password')
            # login
            login = subprocess.run(
                [
                    MEGATOOLS,
                    "ls",
                    "-u",
                    email,
                    "-p",
                    password,
                ],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if "/Root" in login.stdout:
                print("Logged In", email)
            else:
                print("Error", email)


if __name__ == "__main__":
    main()

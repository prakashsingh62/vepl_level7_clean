from __future__ import print_function
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    creds = None

    # If token already exists, reuse it
    if os.path.exists("token.json"):
        print("token.json already exists.")
        return

    # Run local OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)

    # Save the new token
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    print("token.json generated successfully.")

if __name__ == "__main__":
    main()

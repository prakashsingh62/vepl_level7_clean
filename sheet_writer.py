import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ---------------------------------------------------------
# USE TEST SHEET ONLY (Level-6 Testing Mode)
# ---------------------------------------------------------
TEST_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TEST_TAB_NAME = "RFQ TEST SHEET"
SERVICE_ACCOUNT_FILE = "service_account.json"


# ---------------------------------------------------------
# Google Sheets Service
# ---------------------------------------------------------
def get_sheet_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()


# ---------------------------------------------------------
# LEVEL-6 FINAL WRITER FOR PARSED RFQ ROWS
# ---------------------------------------------------------
def write_rfq_rows(rows):
    """
    rows = [
        [date, from, subject, rfq_no, qty, part, description, body, source]
    ]
    """

    try:
        sheet = get_sheet_service()

        sheet.values().append(
            spreadsheetId=TEST_SHEET_ID,
            range=f"{TEST_TAB_NAME}!A2",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

        return True

    except Exception as e:
        return str(e)

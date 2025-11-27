from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from rfq_status_engine import build_rfq_record, parse_date_safe

def read_sheet(sheet_id, tab_name):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    range_name = f"{tab_name}!A1:Z"
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    rows = result.get("values", [])

    if not rows:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    output = []
    for r in data_rows:
        record = build_rfq_record(headers, r)
        output.append(record)

    return output

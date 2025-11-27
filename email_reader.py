import imaplib
import email
from email.header import decode_header
import os
import re
import json
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ---------------------------------------------------------
# CONFIG LOADER
# ---------------------------------------------------------
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print("ERROR loading config.json:", e)
        return {}


# ---------------------------------------------------------
# GMAIL SERVICE
# ---------------------------------------------------------
def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("gmail", "v1", credentials=creds)
    return service


print("### LOADED EMAIL_READER FROM:", __file__)
print("USING NEW GMAIL API READER")


# ---------------------------------------------------------
# HTML → CLEAN TEXT (Medium Clean)
# ---------------------------------------------------------
def clean_html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "img"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\n{2,}', '\n', text)

    return text.strip()


# ---------------------------------------------------------
# CLEAN ONLY THE LATEST MESSAGE FROM EMAIL THREAD
# ---------------------------------------------------------
def extract_latest_message(text):
    if not text:
        return ""

    text = text.replace("\r", "")
    text = re.split(r"\nOn .*wrote:", text, flags=re.IGNORECASE)[0]
    text = re.split(r"\nFrom: ", text)[0]
    text = re.split(r"Original Message", text, flags=re.IGNORECASE)[0]
    text = re.split(r"Regards,|Warm Regards,|Best Regards,|Thanks,|Thank you", text)[0]
    text = re.sub(r"^>+ ?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


# ---------------------------------------------------------
# RFQ EXTRACTOR
# ---------------------------------------------------------
def extract_rfq_data(subject, body):
    text = f"{subject}\n{body}"

    rfq_patterns = [
        r'\bRFQ[:\s-]*([A-Za-z0-9-_/]+)',
        r'\bEnquiry[:\s-]*([A-Za-z0-9-_/]+)',
        r'\bEnq[:\s-]*([A-Za-z0-9-_/]+)',
        r'\bInquiry[:\s-]*([A-Za-z0-9-_/]+)',
        r'\b2800\d{5,}\b'
    ]

    rfq_no = ""
    for p in rfq_patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            rfq_no = match.group(1)
            break

    qty = ""
    qty_match = re.search(r'\b(Qty|Quantity)[:\s]*([\d\.]+)', text, re.IGNORECASE)
    if qty_match:
        qty = qty_match.group(2)

    part = ""
    part_match = re.search(r'(Part\s*Number|Model|PN|Item Code)[:\s-]*([A-Za-z0-9-_/]+)', text, re.IGNORECASE)
    if part_match:
        part = part_match.group(2)

    desc = ""
    desc_match = re.search(r'(Description|Desc)[:\s-]*(.*)', text, re.IGNORECASE)
    if desc_match:
        desc = desc_match.group(2).strip()

    return {
        "rfq_no": rfq_no,
        "qty": qty,
        "part": part,
        "description": desc
    }


# ---------------------------------------------------------
# BASE64URL DECODER FOR GMAIL
# ---------------------------------------------------------
def _b64url_decode(data_str):
    if not data_str:
        return b""
    rem = len(data_str) % 4
    if rem:
        data_str += "=" * (4 - rem)
    return base64.urlsafe_b64decode(data_str.encode("utf-8"))


def _get_header(headers, name):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


# ---------------------------------------------------------
# GMAIL-BASED EMAIL READER (mark-as-read supported)
# ---------------------------------------------------------
def fetch_rfq_emails(max_results=50, unread_only=True, query=None, mark_as_read=False):
    service = get_gmail_service()
    q = ""

    if unread_only:
        q = "is:unread"
    if query:
        q = (q + " " + query).strip()

    res = service.users().messages().list(
        userId="me",
        q=q,
        maxResults=max_results
    ).execute()

    messages = res.get("messages", [])
    parsed = []

    for m in messages:
        mid = m["id"]

        try:
            msg = service.users().messages().get(
                userId="me", id=mid, format="full"
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])
            subject = _get_header(headers, "Subject")
            sender = _get_header(headers, "From")
            date = _get_header(headers, "Date")

            body_text = ""
            payload = msg.get("payload", {})
            mime_type = payload.get("mimeType", "")
            parts = payload.get("parts")

            # BODY HANDLING
            if mime_type == "text/plain" and payload.get("body", {}).get("data"):
                body_text = _b64url_decode(payload["body"]["data"]).decode("utf-8", errors="ignore")

            elif mime_type == "text/html" and payload.get("body", {}).get("data"):
                html = _b64url_decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
                body_text = clean_html_to_text(html)

            elif parts:
                for p in parts:
                    pdata = p.get("body", {}).get("data")
                    ptype = p.get("mimeType", "")

                    if pdata:
                        decoded = _b64url_decode(pdata).decode("utf-8", errors="ignore")
                        if ptype == "text/plain":
                            body_text = decoded
                            break
                        elif ptype == "text/html":
                            body_text = clean_html_to_text(decoded)

            if not body_text:
                body_text = msg.get("snippet", "")

            latest = extract_latest_message(body_text)
            rfq = extract_rfq_data(subject or "", latest or body_text)

            parsed.append({
                "id": mid,
                "subject": subject,
                "from": sender,
                "date": date,
                "raw_body": body_text,
                "latest_message": latest,
                "rfq": rfq
            })

            # ---------------------------
            # MARK AS READ OPTION
            # ---------------------------
            if mark_as_read:
                service.users().messages().modify(
                    userId="me",
                    id=mid,
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()

        except Exception as e:
            print("Error parsing email:", e)
            continue

    return parsed


# ---------------------------------------------------------
# BACKWARD-COMPAT WRAPPER FOR OLD CALLERS
# ---------------------------------------------------------
def read_emails(*args, **kwargs):
    config = load_config()
    mark_flag = config.get("gmail_mark_as_read", False)

    emails = fetch_rfq_emails(
        unread_only=True,
        mark_as_read=mark_flag
    )

    return {"status": "success", "emails": emails}

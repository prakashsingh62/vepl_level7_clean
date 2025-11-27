import re
from datetime import datetime

def parse_email_item(item):
    """
    Convert 1 email dictionary from email_reader.py into
    a structured row ready for Sheet1 (TEST MODE).
    """

    raw_date = item.get("date", "").strip()
    raw_from = item.get("from", "").strip()
    raw_subject = item.get("subject", "").strip()
    raw_body = item.get("body", "").strip()

    # ------------------------------------------------------------
    # CLEAN EMAIL DATE
    # ------------------------------------------------------------
    try:
        clean_date = datetime.strptime(raw_date, "%a, %d %b %Y %H:%M:%S %z")
        email_date = clean_date.strftime("%d-%m-%Y")
    except:
        email_date = raw_date

    # ------------------------------------------------------------
    # EXTRACT RFQ NUMBER (if present)
    # ------------------------------------------------------------
    rfq_no = ""
    match = re.search(r"(RFQ|Enquiry|Inquiry)[^\d]*(\d+)", raw_subject, re.IGNORECASE)
    if match:
        rfq_no = match.group(2)

    # ------------------------------------------------------------
    # UID GENERATION (TEST SAFE)
    # ------------------------------------------------------------
    uid = f"TEST-{int(datetime.utcnow().timestamp())}"

    # ------------------------------------------------------------
    # CATEGORY DETECTION
    # ------------------------------------------------------------
    s = raw_subject.lower()

    if "rfq" in s or "enquiry" in s or "inquiry" in s:
        category = "RFQ"
    elif "quotation" in s or "quote" in s:
        category = "Quotation"
    elif "follow" in s:
        category = "Follow-up"
    else:
        category = "General"

    # ------------------------------------------------------------
    # TEST MODE RETURN FORMAT
    # (Only first 9 columns used in test)
    # ------------------------------------------------------------
    return [
        email_date,      # A - Date
        raw_from,        # B - From
        raw_subject,     # C - Subject
        rfq_no,          # D - RFQ No
        uid,             # E - UID
        category,        # F - Category
        "",              # G - Priority (not used in test)
        "",              # H - Status (not used in test)
        raw_body[:200]   # I - Notes (trimmed)
    ]


def parse_email_list(email_list):
    """
    Convert entire list of emails into sheet rows.
    """
    rows = []

    for item in email_list:
        rows.append(parse_email_item(item))

    return rows

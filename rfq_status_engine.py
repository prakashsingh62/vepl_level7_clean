from datetime import datetime

# ---------------------------------------------------------
# MULTI-FORMAT SAFE DATE PARSER
# ---------------------------------------------------------
def parse_date_safe(date_str):
    if not date_str or date_str.strip() == "":
        return None

    date_str = date_str.strip()

    formats = [
        "%d/%m/%Y", "%d-%m-%Y",
        "%d.%m.%Y", "%d/%m/%y",
        "%d-%m-%y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue

    return None


# ---------------------------------------------------------
# NORMALIZE SHEET ROW TO CLEAN DICTIONARY
# ---------------------------------------------------------
def normalize_rfq_row(headers, row):
    data = {}
    for i, h in enumerate(headers):
        key = h.strip().lower().replace(" ", "_").replace(".", "").replace("-", "_")

        # handle duplicates gracefully
        if key in data:
            key = key + "_2"

        data[key] = row[i] if i < len(row) else ""

    return data


# ---------------------------------------------------------
# STATUS ENGINE (LEVEL-7)
# ---------------------------------------------------------
def compute_status(r):
    # PRIORITY STATUS ORDER:
    # 1. FINAL STATUS overrides everything
    if r.get("final_status"):
        return r.get("final_status")

    # 2. If VEPL OFFER DATE exists → QUOTATION SENT
    if r.get("vepl_offer_date"):
        return "QUOTATION SENT"

    # 3. Vendor quotation missing → Vendor Pending
    if r.get("vendor_quotation_status", "").strip() == "":
        return "VENDOR PENDING"

    # 4. Post-offer query → Clarification
    if r.get("post_offer_query"):
        return "CLARIFICATION REQUIRED"

    # 5. Default → Pending
    return "PENDING"


# ---------------------------------------------------------
# AGING ENGINE
# ---------------------------------------------------------
def compute_aging(r):
    rfq_date = parse_date_safe(r.get("rfq_date", ""))

    if not rfq_date:
        return None

    today = datetime.now()
    return (today - rfq_date).days


# ---------------------------------------------------------
# FULL ROW EXPORT (for dashboard + reminders)
# ---------------------------------------------------------
def build_rfq_record(headers, row):
    r = normalize_rfq_row(headers, row)

    return {
        "rfq_no": r.get("rfq_no", ""),
        "customer": r.get("customer_name", ""),
        "location": r.get("location", ""),
        "rfq_date": r.get("rfq_date", ""),
        "due_date": r.get("due_date", ""),
        "vendor": r.get("vendor", ""),
        "concern_person": r.get("concern_person", ""),
        "vepl_offer_no": r.get("vepl_offer_no", ""),
        "current_status": compute_status(r),
        "aging_days": compute_aging(r),
        "remarks": r.get("remarks", ""),
        "raw": r   # full dictionary for future logic
    }

# backend_api.py
from flask import Blueprint, jsonify
from sheet_reader import read_sheet
from config.config import CONFIG
from email_reader import read_emails
from email_parser import parse_email_list     # ← ADDED
from sheet_writer import write_rfq_rows       # ← ALREADY CORRECT

api_blueprint = Blueprint("api", __name__)

# ---------------------------------------------------------
# LEVEL-7 ENDPOINT → Read emails → Parse → Write to Sheet
# ---------------------------------------------------------
@api_blueprint.route("/run_rfq", methods=["GET"])
def run_rfq():
    try:
        # 1. READ EMAILS
        email_result = read_emails()
        if email_result.get("status") != "success":
            return jsonify({"status": "error", "message": "Email read failed"})

        emails = email_result.get("emails", [])

        # 2. PARSE EMAILS → ROWS
        parsed_rows = parse_email_list(emails)

        # 3. WRITE ROWS TO SHEET
        write_status = write_rfq_rows(parsed_rows)
        if write_status is not True:
            return jsonify({"status": "error", "message": f"Sheet write error: {write_status}"})

        return jsonify({
            "status": "success",
            "emails_received": len(emails),
            "rows_written": len(parsed_rows)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ---------------------------------------------------------
# GET RFQ STATUS (SHEET READER)
# ---------------------------------------------------------
def api_get_rfq_status():
    try:
        sheet_id = CONFIG["sheet_id"]
        tab_name = CONFIG["sheet_tab_name"]

        rows = read_sheet(sheet_id, tab_name)

        return {"status": "success", "rows": rows}

    except Exception as e:
        return {"status": "error", "message": str(e)}

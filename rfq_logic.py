from datetime import datetime

def process_rfq_data(sheet_values=None, shadow_mode=False):
    """
    Level-6 Shadow Mode + Level-5 compatibility

    sheet_values:
        - Passed when real RFQ data is loaded
    shadow_mode:
        - True when triggered by /api/run_shadow (read-only test)
    """

    # Placeholder logic for now (returns empty sections)
    summary = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "vendor_pending": 0,
        "quotation_received": 0,
        "clarification": 0,
        "post_offer": 0,
        "overdue": 0,
        "client_followup": 0
    }

    return {
        "mode": "shadow" if shadow_mode else "live",
        "summary": summary,
        "high": [],
        "medium": [],
        "low": [],
        "vendor_pending": [],
        "quotation_received": [],
        "clarification": [],
        "post_offer": [],
        "overdue": [],
        "client_followup": []
    }

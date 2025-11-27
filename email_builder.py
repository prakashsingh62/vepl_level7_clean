# email_builder.py
def build_email(rfq_record):
    # simple HTML builder — extend as needed
    subject = f"RFQ {rfq_record.get('rfq')} - Follow up"
    body = f"""
    <p>RFQ: {rfq_record.get('rfq')}</p>
    <p>Client: {rfq_record.get('client')}</p>
    <p>Vendor: {rfq_record.get('vendor')}</p>
    <p>Current status: {rfq_record.get('current')}</p>
    """
    return subject, body

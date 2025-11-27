from flask import Flask
from backend_api import api_blueprint, api_get_rfq_status

app = Flask(__name__)

# Register API blueprint
app.register_blueprint(api_blueprint, url_prefix="/api")

@app.route("/")
def home():
    return "RFQ Level 6 Backend is Running"

@app.route("/api/get_rfq_status")
def get_rfq_status():
    from backend_api import api_get_rfq_status
    return api_get_rfq_status()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)


# app.py
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os, hmac, hashlib, base64, requests
from database import init_db, mongo
from zoom_api import get_zoom_access_token

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
init_db(app)

@app.route('/')
def home():
    return jsonify({"message": "Flask + MongoDB connected successfully!"})

@app.route('/add')
def add_data():
    mongo.db.students.insert_one({"name": "Arun", "project": "Zoom Integration"})
    return jsonify({"status": "success", "message": "Data added to MongoDB"})

@app.route('/get')
def get_data():
    data = list(mongo.db.students.find({}, {"_id": 0}))
    return jsonify(data)

@app.route('/create_meeting')
def create_meeting():
    access_token = get_zoom_access_token()
    url = "https://api.zoom.us/v2/users/me/meetings"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"topic": "Test Meeting", "type": 1, "settings": {"join_before_host": True, "approval_type": 0}}

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    mongo.db.meetings.insert_one(result)

    return jsonify({"status": "created", "meeting_id": result.get("id"), "join_url": result.get("join_url")})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    
    if data and "plainToken" in data:
        plain_token = data["plainToken"]
        secret_token = os.getenv("ZOOM_VERIFICATION_TOKEN")
        if not secret_token:
            return "Missing ZOOM_VERIFICATION_TOKEN", 500
        
        encrypted_token = base64.b64encode(
            hmac.new(
                secret_token.encode(),
                plain_token.encode(),
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

        return jsonify({
            "plainToken": plain_token,
            "encryptedToken": encrypted_token
        })
    
    # Normal event
    print("Received event:", data)
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

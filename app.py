from flask import Flask, request, jsonify
import os, hmac, hashlib, base64
from database import init_db, mongo

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
init_db(app)

@app.route("/")
def home():
    return jsonify({"message": "Flask + MongoDB connected"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "plainToken" in data:
        plain_token = data["plainToken"]
        secret_token = os.getenv("ZOOM_VERIFICATION_TOKEN")
        encrypted_token = base64.b64encode(
            hmac.new(secret_token.encode(), plain_token.encode(), hashlib.sha256).digest()
        ).decode("utf-8")
        return jsonify({
            "plainToken": plain_token,
            "encryptedToken": encrypted_token
        })

    print("Received Zoom event:", data)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

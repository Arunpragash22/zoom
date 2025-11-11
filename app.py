from flask import Flask, request, jsonify
import os, hmac, hashlib, base64

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    if data and "plainToken" in data:
        plain_token = data["plainToken"]
        secret_token = os.getenv("ZOOM_VERIFICATION_TOKEN")
        encrypted_token = base64.b64encode(
            hmac.new(secret_token.encode(), plain_token.encode(), hashlib.sha256).digest()
        ).decode("utf-8")
        return jsonify({
            "plainToken": plain_token,
            "encryptedToken": encrypted_token
        })
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

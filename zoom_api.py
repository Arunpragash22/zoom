import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    data = {"grant_type": "account_credentials", "account_id": os.getenv("ZOOM_ACCOUNT_ID")}
    auth = (os.getenv("ZOOM_CLIENT_ID"), os.getenv("ZOOM_CLIENT_SECRET"))

    try:
        response = requests.post(url, data=data, auth=auth)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print("Failed to get Zoom access token:", e)
        return None

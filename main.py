import os
import requests
from datetime import datetime

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_TOKEN = os.environ["TWITCH_TOKEN"]

CHANNEL_NAME = "warframe"


def get_headers():
    return {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_TOKEN}"
    }


def get_broadcaster_id():
    url = f"https://api.twitch.tv/helix/users?login=warframe"

    r = requests.get(url, headers=get_headers())
    data = r.json()

    print("USER API RESPONSE:", data)

    if "data" not in data or len(data["data"]) == 0:
        raise Exception("Failed to fetch broadcaster ID")

    return data["data"][0]["id"]


def get_schedule():
    broadcaster_id = get_broadcaster_id()

    print("BROADCASTER ID:", broadcaster_id)

    url = f"https://api.twitch.tv/helix/schedule?broadcaster_id={broadcaster_id}"

    r = requests.get(url, headers=get_headers())

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    r.raise_for_status()

    return r.json().get("data", {}).get("segments", [])
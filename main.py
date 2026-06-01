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
    url = f"https://api.twitch.tv/helix/users?login={CHANNEL_NAME}"
    r = requests.get(url, headers=get_headers())
    data = r.json()
    return data["data"][0]["id"]


def get_schedule():
    broadcaster_id = get_broadcaster_id()

    url = f"https://api.twitch.tv/helix/schedule?broadcaster_id={broadcaster_id}"

    r = requests.get(url, headers=get_headers())

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    r.raise_for_status()

    return r.json().get("data", {}).get("segments", [])


segments = get_schedule()
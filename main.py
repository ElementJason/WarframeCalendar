import os
import requests
from datetime import datetime

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_TOKEN = os.environ["TWITCH_TOKEN"]
BROADCASTER_ID = os.environ["TWITCH_BROADCASTER_ID"]

def get_schedule():
    url = f"https://api.twitch.tv/helix/schedule?broadcaster_id={BROADCASTER_ID}"

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_TOKEN}"
    }

    r = requests.get(url, headers=headers)

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    r.raise_for_status()

    data = r.json()

    return data.get("data", {}).get("segments", [])

def dt_to_ics(dt):
    return datetime.fromisoformat(
        dt.replace("Z", "+00:00")
    ).strftime("%Y%m%dT%H%M%SZ")

segments = get_schedule()

ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Twitch Schedule Sync//EN"
]

for s in segments:
    ics.extend([
        "BEGIN:VEVENT",
        f"UID:{s['id']}",
        f"SUMMARY:{s['title']}",
        f"DTSTART:{dt_to_ics(s['start_time'])}",
        f"DTEND:{dt_to_ics(s['end_time'])}",
        "END:VEVENT"
    ])

ics.append("END:VCALENDAR")

with open("calendar.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(ics))
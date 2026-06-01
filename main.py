import os
import requests

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_TOKEN = os.environ["TWITCH_TOKEN"]

CHANNEL = "warframe"


def headers():
    return {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_TOKEN}"
    }


def get_schedule():
    # get user id
    user = requests.get(
        f"https://api.twitch.tv/helix/users?login={CHANNEL}",
        headers=headers()
    ).json()

    print("USER RESPONSE:", user)

    if not user.get("data"):
        return []

    user_id = user["data"][0]["id"]
    print("USER ID:", user_id)

    # get schedule
    sched = requests.get(
        f"https://api.twitch.tv/helix/schedule?broadcaster_id={user_id}",
        headers=headers()
    )

    print("SCHEDULE STATUS:", sched.status_code)
    print("SCHEDULE TEXT:", sched.text)

    if sched.status_code != 200:
        return []

    return sched.json().get("data", {}).get("segments", [])


segments = get_schedule()

def to_ics_time(dt):
    # Converts: 2026-06-02T18:00:00Z → 20260602T180000Z
    return (
        dt.replace("-", "")
          .replace(":", "")
          .replace(".000", "")
          .replace("Z", "")
        + "Z"
    )


# ALWAYS create file even if empty
ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "PRODID:-//Twitch Calendar//EN"
]

for s in segments:
    start = to_ics_time(s.get("start_time", ""))
    end = to_ics_time(s.get("end_time", ""))

    ics.append("BEGIN:VEVENT")
    ics.append(f"UID:{s.get('id','no-id')}")
    ics.append(f"SUMMARY:{s.get('title','Twitch Stream')}")

    ics.append(f"DTSTART:{start}")
    ics.append(f"DTEND:{end}")

    ics.append("END:VEVENT")

ics.append("END:VCALENDAR")

with open("calendar.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(ics))

print("calendar.ics CREATED with", len(segments), "events")
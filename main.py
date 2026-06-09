import os
import requests

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_TOKEN = os.environ["TWITCH_TOKEN"]

# 👉 Add more channels here anytime
CHANNELS = [
    "warframe"
    "warframeinternational"
]


def headers():
    return {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_TOKEN}"
    }


def get_user_id(channel):
    user = requests.get(
        f"https://api.twitch.tv/helix/users?login={channel}",
        headers=headers()
    ).json()

    print(f"USER RESPONSE ({channel}):", user)

    if not user.get("data"):
        return None

    return user["data"][0]["id"]


def get_schedule_for_user(user_id, channel):
    sched = requests.get(
        f"https://api.twitch.tv/helix/schedule?broadcaster_id={user_id}",
        headers=headers()
    )

    print(f"SCHEDULE STATUS ({channel}):", sched.status_code)
    print(f"SCHEDULE TEXT ({channel}):", sched.text)

    if sched.status_code != 200:
        return []

    segments = sched.json().get("data", {}).get("segments", [])

    # tag channel into event
    for s in segments:
        s["channel"] = channel

    return segments


def get_all_segments():
    all_segments = []

    for channel in CHANNELS:
        user_id = get_user_id(channel)

        if not user_id:
            print(f"Skipping {channel} (no user id)")
            continue

        segments = get_schedule_for_user(user_id, channel)
        all_segments.extend(segments)

    return all_segments


def to_ics_time(dt):
    return (
        dt.replace("-", "")
          .replace(":", "")
          .replace(".000", "")
          .replace("Z", "")
        + "Z"
    )


segments = get_all_segments()


# ALWAYS create file even if empty
ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "PRODID:-//Twitch Calendar//EN",
    "X-WR-TIMEZONE:UTC"
]

for s in segments:
    start = to_ics_time(s.get("start_time", ""))
    end = to_ics_time(s.get("end_time", ""))

    channel = s.get("channel", "unknown")

    ics.append("BEGIN:VEVENT")
    ics.append(f"UID:{s.get('id','no-id')}")
    ics.append(f"SUMMARY:{channel} - {s.get('title','Twitch Stream')}")
    ics.append(f"DTSTART:{start}")
    ics.append(f"DTEND:{end}")
    ics.append("END:VEVENT")

ics.append("END:VCALENDAR")

with open("calendar.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(ics))

print("calendar.ics CREATED with", len(segments), "events")
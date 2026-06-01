import os
import requests
from datetime import datetime
from dateutil import parser
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_TOKEN = os.environ["TWITCH_TOKEN"]
BROADCASTER_ID = os.environ["TWITCH_BROADCASTER_ID"]

CALENDAR_ID = os.environ["GOOGLE_CALENDAR_ID"]
SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def twitch_headers():
    return {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_TOKEN}"
    }


def get_schedule():
    url = f"https://api.twitch.tv/helix/schedule?broadcaster_id={BROADCASTER_ID}"
    r = requests.get(url, headers=twitch_headers())
    r.raise_for_status()
    return r.json()["data"]["segments"]


def calendar_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)


def list_existing_events(service):
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        maxResults=2500,
        singleEvents=True
    ).execute()

    return events_result.get("items", [])


def normalize(title, start):
    return f"{title}-{start}"


def sync():
    service = calendar_service()
    segments = get_schedule()
    existing = list_existing_events(service)

    # map existing events for dedupe/update
    existing_map = {}
    for e in existing:
        key = e.get("extendedProperties", {}).get("private", {}).get("twitch_id")
        if key:
            existing_map[key] = e

    for s in segments:
        start = s["start_time"]
        end = s["end_time"]
        title = s["title"]

        twitch_id = s["id"]

        event_body = {
            "summary": f"Twitch: {title}",
            "start": {"dateTime": start},
            "end": {"dateTime": end},
            "description": "Auto-synced from Twitch schedule",
            "extendedProperties": {
                "private": {
                    "twitch_id": twitch_id
                }
            }
        }

        if twitch_id in existing_map:
            # update if exists
            event_id = existing_map[twitch_id]["id"]
            service.events().update(
                calendarId=CALENDAR_ID,
                eventId=event_id,
                body=event_body
            ).execute()
        else:
            # create new
            service.events().insert(
                calendarId=CALENDAR_ID,
                body=event_body
            ).execute()


if __name__ == "__main__":
    sync()
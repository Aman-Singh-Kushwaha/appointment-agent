
import os
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Scopes for Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "backend/credentials.json"

# Get calendar ID from environment variable
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

def get_calendar_service():
    """Authenticates with the Google Calendar API and returns a service object."""
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=creds)
    return service

def check_availability(start_time: str, end_time: str) -> list[str]:
    """Checks for available time slots in the calendar between two datetimes."""
    service = get_calendar_service()
    start_time_dt = datetime.fromisoformat(start_time)
    end_time_dt = datetime.fromisoformat(end_time)

    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_dt.isoformat() + "Z",
            timeMax=end_time_dt.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    available_slots = []
    current_time = start_time_dt
    while current_time + timedelta(minutes=30) <= end_time_dt:
        slot_end_time = current_time + timedelta(minutes=30)
        is_slot_free = True
        for event in events:
            event_start_str = event["start"].get("dateTime", event["start"].get("date"))
            event_end_str = event["end"].get("dateTime", event["end"].get("date"))

            event_start = datetime.fromisoformat(event_start_str) if "dateTime" in event["start"] else datetime.fromisoformat(event_start_str + "T00:00:00")
            event_end = datetime.fromisoformat(event_end_str) if "dateTime" in event["end"] else datetime.fromisoformat(event_end_str + "T23:59:59")

            # Check for overlap
            if not (slot_end_time <= event_start or current_time >= event_end):
                is_slot_free = False
                break
        
        if is_slot_free:
            available_slots.append(current_time.isoformat())
        
        current_time += timedelta(minutes=30)
    print(f"Available slots: {available_slots}")  # Print available slots for debugging
    return available_slots

def create_appointment(start_time: str, end_time: str, summary: str) -> str:
    """Creates a new event in the calendar."""
    service = get_calendar_service()
    start_time_dt = datetime.fromisoformat(start_time)
    end_time_dt = datetime.fromisoformat(end_time)

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time_dt.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time_dt.isoformat(),
            "timeZone": "UTC",
        },
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

    # Extracting the event link from event object
    event_link = created_event.get('htmlLink')
    
    return f"Appointment created: {event_link}"

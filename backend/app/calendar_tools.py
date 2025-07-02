import os
from datetime import datetime, timedelta, timezone
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
    
    # Ensure input datetimes are timezone-aware UTC
    start_time_dt = datetime.fromisoformat(start_time)
    if start_time_dt.tzinfo is None:
        start_time_dt = start_time_dt.replace(tzinfo=timezone.utc)
    else:
        start_time_dt = start_time_dt.astimezone(timezone.utc)

    end_time_dt = datetime.fromisoformat(end_time)
    if end_time_dt.tzinfo is None:
        end_time_dt = end_time_dt.replace(tzinfo=timezone.utc)
    else:
        end_time_dt = end_time_dt.astimezone(timezone.utc)

    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_dt.isoformat(),
            timeMax=end_time_dt.isoformat(),
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

            # Convert event times to timezone-aware UTC
            if "dateTime" in event["start"]:
                event_start = datetime.fromisoformat(event_start_str)
                if event_start.tzinfo is None:
                    event_start = event_start.replace(tzinfo=timezone.utc)
                else:
                    event_start = event_start.astimezone(timezone.utc)
            else: # Date-only event, assume whole day in UTC
                event_start = datetime.fromisoformat(event_start_str + "T00:00:00").replace(tzinfo=timezone.utc)

            if "dateTime" in event["end"]:
                event_end = datetime.fromisoformat(event_end_str)
                if event_end.tzinfo is None:
                    event_end = event_end.replace(tzinfo=timezone.utc)
                else:
                    event_end = event_end.astimezone(timezone.utc)
            else: # Date-only event, assume whole day in UTC
                event_end = datetime.fromisoformat(event_end_str + "T23:59:59").replace(tzinfo=timezone.utc)

            # Check for overlap
            if not (slot_end_time <= event_start or current_time >= event_end):
                is_slot_free = False
                break
        
        if is_slot_free:
            available_slots.append(current_time.isoformat())
        
        current_time += timedelta(minutes=30)

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
    print(f"Created Event: {created_event}") # Print the full event object
    
    # Construct a generic Google Calendar event link using the event ID and calendar ID
    event_id = created_event.get('id')
    calendar_id_encoded = CALENDAR_ID.replace('@', '%40') # Encode @ for URL
    generic_link = f"https://calendar.google.com/calendar/event?eid={event_id}"

    return f"Appointment created: {generic_link}"
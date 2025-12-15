from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import uuid
from datetime import datetime

def create_calendar_event(creds: Credentials, event_data: dict):
    service = build('calendar', 'v3', credentials=creds)
    
    # Prepare attendees list
    attendees = [{'email': email} for email in event_data.get('attendees', [])]
    
    event_body = {
        'summary': event_data['summary'],
        'start': {
            'dateTime': event_data['start_time'].isoformat(),
            'timeZone': event_data['time_zone'],
        },
        'end': {
            'dateTime': event_data['end_time'].isoformat(),
            'timeZone': event_data['time_zone'],
        },
        'attendees': attendees,
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 5}
            ]
        }
    }
    
    event = service.events().insert(
        calendarId='primary',
        body=event_body,
        conferenceDataVersion=1,
        sendUpdates='all'
    ).execute()
    
    return event

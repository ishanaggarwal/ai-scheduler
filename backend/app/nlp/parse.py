import re
import dateparser
from datetime import datetime, timedelta
import pytz
from pydantic import BaseModel
from typing import List, Optional

class ParseResult(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime
    time_zone: str
    attendees: List[str]
    original_command: str

def extract_emails(text: str) -> List[str]:
    email_regex = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.findall(email_regex, text)

def extract_duration(text: str) -> int:
    # Default 30 mins
    duration = 30
    
    # Regex for "X min", "X minutes", "X h", "X hour"
    min_regex = r'(\d+)\s*(?:min|mins|minutes)'
    hour_regex = r'(\d+)\s*(?:h|hr|hrs|hours)'
    
    min_match = re.search(min_regex, text, re.IGNORECASE)
    hour_match = re.search(hour_regex, text, re.IGNORECASE)
    
    if min_match:
        duration = int(min_match.group(1))
    elif hour_match:
        duration = int(hour_match.group(1)) * 60
        
    return duration

def parse_command(command: str, default_tz: str = "America/Los_Angeles") -> ParseResult:
    # 1. Extract emails
    attendees = extract_emails(command)
    
    # 2. Extract duration
    duration_minutes = extract_duration(command)
    
    # 3. Extract Date/Time
    # We use dateparser to find the date string.
    # Since dateparser.parse returns a datetime object, we can use it directly.
    # We'll try to parse the command to find a date.
    
    settings = {
        'PREFER_DATES_FROM': 'future',
        'TIMEZONE': default_tz,
        'RETURN_AS_TIMEZONE_AWARE': True
    }
    
    # Remove emails from command to avoid confusing dateparser (sometimes emails contain numbers/dates)
    clean_command = command
    for email in attendees:
        clean_command = clean_command.replace(email, "")
        
    # Remove duration from command
    # This is a bit tricky as we want to keep the rest of the text for summary
    # For now, we'll just pass the clean_command to dateparser
    
    start_dt = dateparser.parse(clean_command, settings=settings)
    
    if not start_dt:
        # Fallback: try to find "tomorrow" or "next monday" etc explicitly if dateparser failed on the whole string
        # But dateparser is usually good at extracting date from text.
        # If it fails, default to tomorrow 9am
        tz = pytz.timezone(default_tz)
        now = datetime.now(tz)
        start_dt = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Ensure timezone
    if start_dt.tzinfo is None:
        tz = pytz.timezone(default_tz)
        start_dt = tz.localize(start_dt)
        
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    
    # 4. Extract Summary
    # The summary is the command minus the date/time/emails/duration keywords
    # This is hard to do perfectly without a complex NLP model.
    # For this agent, we will use the full command as the description, 
    # and try to extract a "title" if possible, or just use "Meeting" + attendees
    
    # Simple heuristic: Use the whole command as summary for now, or try to strip known parts.
    # A better approach: "Meeting with [Attendees]" or just the command.
    
    summary = command
    # If there is a "about" or "for" keyword, take everything after it as the title
    match = re.search(r'\b(about|for|:)\s+(.*)', command, re.IGNORECASE)
    if match:
        summary = match.group(2).strip()
    else:
        # If no specific topic, construct one
        if attendees:
            summary = f"Meeting with {', '.join(attendees)}"
        else:
            summary = "Meeting"

    return ParseResult(
        summary=summary,
        start_time=start_dt,
        end_time=end_dt,
        time_zone=str(start_dt.tzinfo),
        attendees=attendees,
        original_command=command
    )

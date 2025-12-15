from app.nlp.parse import parse_command
from datetime import datetime, timedelta
import pytest

def test_parse_simple_command():
    cmd = "Meeting with alice@example.com tomorrow 10am"
    result = parse_command(cmd)
    
    assert "alice@example.com" in result.attendees
    assert result.summary.strip() == "Meeting with" or "Meeting" in result.summary
    # Date checks are tricky with relative time, but we can check if it's in the future
    assert result.start_time > datetime.now(result.start_time.tzinfo)

def test_parse_duration():
    cmd = "Sync 45 mins"
    result = parse_command(cmd)
    duration = (result.end_time - result.start_time).total_seconds() / 60
    assert duration == 45

def test_parse_explicit_timezone():
    cmd = "Call 3pm PST"
    result = parse_command(cmd)
    assert str(result.start_time.tzinfo) == "America/Los_Angeles" or "PST" in str(result.start_time.tzinfo)

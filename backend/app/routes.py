from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, JSONResponse
from app.db import get_db
from app.models import User, Event
from app.nlp.parse import parse_command, ParseResult
from app.google.auth import get_flow, get_credentials, encrypt_token, decrypt_token
from app.google.calendar import create_calendar_event
from app.config import get_settings
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter()
settings = get_settings()

class ScheduleRequest(BaseModel):
    command: str
    
class ScheduleResponse(BaseModel):
    eventId: str
    htmlLink: str
    meetLink: Optional[str]
    summary: str
    start: datetime
    end: datetime
    attendees: List[str]

# Dependency to get current user from session/cookie
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/auth/start")
def auth_start():
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return {"url": authorization_url}

@router.get("/auth/callback")
def auth_callback(request: Request, code: str, db: Session = Depends(get_db)):
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # Get user info
    from googleapiclient.discovery import build
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    email = user_info['email']
    
    # Store user and tokens
    user = db.query(User).filter(User.email == email).first()
    
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    
    encrypted_token = encrypt_token(token_data)
    
    if not user:
        user = User(email=email, refresh_token_encrypted=encrypted_token)
        db.add(user)
    else:
        user.refresh_token_encrypted = encrypted_token
        
    db.commit()
    db.refresh(user)
    
    response = RedirectResponse(url=f"{settings.APP_BASE_URL}")
    response.set_cookie(key="user_id", value=str(user.id), httponly=True, samesite='lax')
    return response

@router.get("/auth/me")
def auth_me(user: User = Depends(get_current_user)):
    if not user:
        return JSONResponse(status_code=401, content={"authenticated": False})
    return {"authenticated": True, "email": user.email}

@router.post("/api/parse", response_model=ParseResult)
def parse_endpoint(request: ScheduleRequest):
    return parse_command(request.command)

@router.post("/api/schedule", response_model=ScheduleResponse)
def schedule_endpoint(request: ScheduleRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    # 1. Parse
    parsed = parse_command(request.command)
    
    # 2. Get Credentials
    token_data = decrypt_token(user.refresh_token_encrypted)
    creds = get_credentials(token_data)
    
    # 3. Create Event
    event_data = parsed.dict()
    try:
        g_event = create_calendar_event(creds, event_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 4. Save to DB
    meet_link = g_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')
    
    new_event = Event(
        google_event_id=g_event['id'],
        summary=g_event['summary'],
        start_time=parsed.start_time,
        end_time=parsed.end_time,
        meet_link=meet_link,
        html_link=g_event.get('htmlLink'),
        attendees_count=len(parsed.attendees)
    )
    db.add(new_event)
    db.commit()
    
    return ScheduleResponse(
        eventId=g_event['id'],
        htmlLink=g_event.get('htmlLink'),
        meetLink=meet_link,
        summary=g_event['summary'],
        start=parsed.start_time,
        end=parsed.end_time,
        attendees=parsed.attendees
    )

@router.get("/api/history")
def history_endpoint(db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.created_at.desc()).limit(10).all()
    return events

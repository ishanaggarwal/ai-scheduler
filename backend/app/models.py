from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    google_event_id = Column(String, index=True)
    summary = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    meet_link = Column(String, nullable=True)
    html_link = Column(String, nullable=True)
    attendees_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # In a real multi-user app, we'd link this to User
    # user_id = Column(Integer, ForeignKey("users.id"))

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.config import get_settings
from cryptography.fernet import Fernet
import json

settings = get_settings()

SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

def get_fernet():
    return Fernet(settings.APP_ENCRYPTION_KEY.encode())

def encrypt_token(token_data: dict) -> str:
    f = get_fernet()
    return f.encrypt(json.dumps(token_data).encode()).decode()

def decrypt_token(encrypted_token: str) -> dict:
    f = get_fernet()
    return json.loads(f.decrypt(encrypted_token.encode()).decode())

def get_flow(redirect_uri: str = None):
    if not redirect_uri:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_credentials(token_data: dict) -> Credentials:
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

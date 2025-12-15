# AI Scheduler (AGENTIC AI)

A production-ready AI scheduling agent that creates Google Calendar events with Google Meet links from natural language commands.

## Features

- **Natural Language Parsing**: Understands commands like "Schedule a 30 min meet tomorrow 3pm with john@example.com".
- **Google Calendar Integration**: Creates events, attaches Meet links, and sends invites.
- **Reminders**: Configures email reminders 5 minutes before the meeting.
- **Real-time UI**: Next.js + Tailwind CSS frontend with live parsing preview.
- **Secure**: OAuth2 authentication, encrypted tokens, no secrets in code.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Google APIs
- **Frontend**: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- **Database**: SQLite (local), Postgres (production)
- **Deployment**: Google Cloud Run, GitHub Actions

## Setup Instructions

### 1. Google Cloud Setup

1. Create a new Google Cloud Project.
2. Enable the **Google Calendar API** and **Google People API** (for user info).
3. Configure **OAuth Consent Screen**:
   - User Type: External (or Internal if using Workspace)
   - Scopes: `.../auth/calendar.events`, `.../auth/userinfo.email`, `openid`
   - Add Test Users: `ishanaggarwal888@gmail.com`
4. Create **OAuth 2.0 Client ID**:
   - Application Type: Web application
   - Authorized Redirect URIs:
     - Local: `http://localhost:8000/auth/callback`
     - Production: `https://<YOUR-CLOUD-RUN-URL>/auth/callback`
5. Download the JSON credentials or copy Client ID and Secret.

### 2. Local Development

1. Clone the repository.
2. Create a `.env` file in `backend/` (see `.env.example`).
   ```bash
   APP_BASE_URL=http://localhost:3000
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   APP_ENCRYPTION_KEY=your_generated_key_32_bytes_base64
   DATABASE_URL=sqlite:///./scheduler.db
   ```
   To generate `APP_ENCRYPTION_KEY`:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Open `http://localhost:3000`.

### 3. Deployment (Google Cloud Run)

1. Set up **Workload Identity Federation** for GitHub Actions.
2. Add the following **GitHub Secrets**:
   - `GCP_PROJECT_ID`
   - `GCP_REGION`
   - `CLOUD_RUN_SERVICE`
   - `WIF_PROVIDER`
   - `WIF_SERVICE_ACCOUNT`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `APP_BASE_URL` (Your Cloud Run URL)
   - `APP_ENCRYPTION_KEY`
   - `DATABASE_URL` (Connection string to Cloud SQL or other Postgres)

3. Push to `main` branch to deploy.

## API Usage

### Parse Command
```bash
curl -X POST http://localhost:8000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"command": "Schedule a meeting tomorrow at 2pm"}'
```

### Schedule Event (Requires Auth Cookie)
```bash
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -b "user_id=..." \
  -d '{"command": "Schedule a meeting tomorrow at 2pm"}'
```

## Verification

1. Log in with Google.
2. Type a command.
3. Click Schedule.
4. Check Google Calendar for the new event with Meet link.
5. Verify email reminder setting in the event details.

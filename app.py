import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import logging
import json
import os
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Configure Gemini API
# 🔹 Gemini API Configuration
GEMINI_API_KEY = "AIzaSyACqjXQAfqP2NX3pcAwdbQ3XX_-Z_MJZqY"  # Replace with actual key
try:
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel('gemini-1.5-flash-001-tuning')
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}. Please check your API key.")
    logger.error(f"Gemini API config error: {e}")
    llm = None

# 🔹 Configure Supabase
SUPABASE_URL = "https://hvbzuubgxfobyfgchgpr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2Ynp1dWJneGZvYnlmZ2NoZ3ByIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0MDEwMTIsImV4cCI6MjA2Mjk3NzAxMn0.YJA-rpFVVIaYjqCULSgvepGYyGynrIUF1pksjHAaJhI"
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    supabase.table("meetings").select("*").limit(1).execute()
except Exception as e:
    st.error(f"Supabase connection failed: {e}")
    supabase = None

# 🔹 Google Calendar API Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_calendar_service():
    """Authenticate and return Google Calendar service."""
    if not os.path.exists(CREDENTIALS_FILE):
        st.error("Missing credentials.json. Please download it from Google Cloud Console.")
        return None
    try:
        creds = None
        if os.path.exists(TOKEN_FILE):
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Failed to authenticate with Google Calendar: {e}")
        logger.error(f"Calendar auth error: {e}")
        return None

# 🔹 Streamlit App Configuration
st.set_page_config(page_title="Agentic Meeting Scheduler", layout="wide")
st.title("📅 Agentic Meeting Scheduler")
st.markdown("""
Chat with our AI-powered assistant to schedule meetings seamlessly. Select a date, time, and timezone, provide details, and the bot will add the event to your Google Calendar with email notifications.  
**Current Date and Time: May 16, 2025, 07:44 PM IST**
""")

# 🔹 Initialize Session State
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'meeting_details' not in st.session_state:
    st.session_state.meeting_details = {}
if 'calendar_service' not in st.session_state:
    st.session_state.calendar_service = None

# 🔹 Helper Functions
def get_gemini_response(prompt):
    """Generate response using Gemini."""
    if not llm:
        return "Gemini API not initialized."
    try:
        response = llm.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        return "Failed to generate response."
    except Exception as e:
        logger.error(f"Gemini response failed: {str(e)}")
        return f"Error: {str(e)}"

def schedule_meeting(details):
    """Schedule a meeting in Google Calendar and store in Supabase."""
    try:
        service = st.session_state.calendar_service or get_calendar_service()
        if not service:
            return None
        st.session_state.calendar_service = service

        # Combine description and agenda
        description = details.get('description', '')
        agenda = details.get('agenda', '')
        if agenda:
            description = f"{description}\n\nAgenda: {agenda}" if description else f"Agenda: {agenda}"

        event = {
            'summary': details.get('title', 'Meeting'),
            'description': description,
            'start': {
                'dateTime': details['start_time'].isoformat(),
                'timeZone': details.get('timezone', 'Asia/Kolkata'),
            },
            'end': {
                'dateTime': (details['start_time'] + timedelta(minutes=60)).isoformat(),
                'timeZone': details.get('timezone', 'Asia/Kolkata'),
            },
            'attendees': [{'email': email} for email in details.get('attendees', [])],
            'visibility': 'default',
            'status': 'confirmed',
            'reminders': {
                'useDefault': True
            }
        }
        event = service.events().insert(
            calendarId='primary',
            body=event,
            sendNotifications=True
        ).execute()
        logger.info(f"Event created: {event['id']}, Summary: {event['summary']}, Start: {event['start']['dateTime']}")

        # Store in Supabase
        if supabase:
            try:
                supabase.table("meetings").insert({
                    'event_id': event['id'],
                    'title': details['title'],
                    'start_time': details['start_time'].isoformat(),
                    'description': details.get('description', ''),
                    'attendees': details.get('attendees', []),
                    'agenda': agenda
                }).execute()
            except Exception as e:
                logger.error(f"Supabase insert failed: {str(e)}")
                st.warning("Meeting scheduled, but failed to store in Supabase.")

        return event['id']
    except Exception as e:
        logger.error(f"Meeting scheduling failed: {str(e)}")
        st.error(f"Failed to schedule meeting: {str(e)}")
        return None

# 🔹 Sidebar for Meeting Selection
with st.sidebar:
    st.header("Schedule a Meeting")
    meeting_date = st.date_input("Select Date", min_value=datetime(2025, 5, 16))
    meeting_time = st.time_input("Select Time")
    timezone = st.selectbox("Timezone", ["Asia/Kolkata"] + [tz for tz in pytz.all_timezones if tz != "Asia/Kolkata"], index=0)
    meeting_title = st.text_input("Meeting Title", "Team Meeting")
    meeting_description = st.text_area("Description (Optional)")
    meeting_agenda = st.text_area("Meeting Agenda (Optional)")
    meeting_attendees = st.text_input("Attendees (comma-separated emails)")
    if st.button("Propose Meeting"):
        start_time = datetime.combine(meeting_date, meeting_time).replace(tzinfo=pytz.timezone(timezone))
        attendees = [email.strip() for email in meeting_attendees.split(',') if email.strip()]
        st.session_state.meeting_details = {
            'title': meeting_title,
            'description': meeting_description,
            'agenda': meeting_agenda,
            'start_time': start_time,
            'attendees': attendees,
            'timezone': timezone
        }
        st.session_state.chat_history.append({
            'role': 'user',
            'message': f"Proposed meeting: {meeting_title} on {start_time.strftime('%Y-%m-%d %H:%M')} {timezone} with {', '.join(attendees)}"
        })
        # Gemini confirms details
        prompt = f"""
        A user has proposed a meeting titled "{meeting_title}" on {start_time.strftime('%Y-%m-%d %H:%M')} {timezone} with attendees {', '.join(attendees)}.
        Description: {meeting_description}
        Agenda: {meeting_agenda}
        Confirm the details and ask if they want to proceed with scheduling or make changes.
        Keep the tone professional and concise.
        """
        response = get_gemini_response(prompt)
        st.session_state.chat_history.append({'role': 'Response', 'message': response})

# 🔹 Main Chat Interface
st.subheader("Chat with the Scheduler")
chat_container = st.container()
user_input = st.text_input("Your Message", placeholder="e.g., Confirm the meeting or change the time")
if user_input:
    st.session_state.chat_history.append({'role': 'user', 'message': user_input})
    prompt = f"""
    You are a professional meeting scheduler assistant. The user has proposed a meeting with the following details:
    Title: {st.session_state.meeting_details.get('title', 'N/A')}
    Date and Time: {st.session_state.meeting_details.get('start_time', 'N/A')}
    Timezone: {st.session_state.meeting_details.get('timezone', 'N/A')}
    Description: {st.session_state.meeting_details.get('description', 'N/A')}
    Agenda: {st.session_state.meeting_details.get('agenda', 'N/A')}
    Attendees: {', '.join(st.session_state.meeting_details.get('attendees', []))}

    The user's latest message is: "{user_input}"

    Respond appropriately:
    - If the user confirms, schedule the meeting and confirm completion.
    - If the user requests changes, suggest how to update via the sidebar.
    - If unclear, ask for clarification.
    Keep the tone professional and concise.
    """
    response = get_gemini_response(prompt)
    st.session_state.chat_history.append({'role': 'Response', 'message': response})

    # Check if user confirmed scheduling
    if "confirm" in user_input.lower() and st.session_state.meeting_details:
        with st.spinner("Scheduling meeting..."):
            event_id = schedule_meeting(st.session_state.meeting_details)
            if event_id:
                st.session_state.chat_history.append({
                    'role': 'Response',
                    'message': f"Meeting scheduled successfully! Event ID: {event_id}. Check your Google Calendar and email for confirmation."
                })
                st.session_state.meeting_details = {}  # Clear details after scheduling
            else:
                st.session_state.chat_history.append({
                    'role': 'Response',
                    'message': "Failed to schedule meeting. Please check your Google Calendar credentials and try again."
                })

# 🔹 Display Chat History
with chat_container:
    for chat in st.session_state.chat_history:
        if chat['role'] == 'user':
            st.markdown(f"**You**: {chat['message']}")
        else:
            st.markdown(f"**Response**: {chat['message']}")

# 🔹 Footer
st.markdown("---")
st.markdown("""
*Built with Streamlit, Google Gemini, Google Calendar API, and Supabase*  
*Developed for seamless meeting scheduling*  
*Date: May 16, 2025*  
*Troubleshooting: If the meeting doesn't appear, check your Google Calendar's primary calendar, timezone, and email notifications. Ensure credentials.json is valid.*
""")
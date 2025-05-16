Agentic Meeting Scheduler
A Streamlit-based web application for scheduling meetings using a conversational AI chatbot. Powered by Google Gemini, it integrates with Google Calendar API to create events and Supabase for persistent storage. Users can propose meetings with details like date, time, timezone, title, description, agenda, and attendees, and the chatbot confirms before scheduling.
Features

Conversational AI: Propose and confirm meetings via a Google Gemini-powered chatbot.
Google Calendar Integration: Add events to the primary calendar with email notifications.
Supabase Storage: Store meeting details (event ID, title, start time, description, agenda, attendees).
Agenda Support: Include a custom meeting agenda in the event description and database.
Timezone Flexibility: Supports all pytz timezones, defaulting to Asia/Kolkata.
Error Handling: Manages invalid inputs, API failures, and authentication issues.
User-Friendly UI: Streamlit interface with sidebar inputs and chat history.

Prerequisites

Python 3.8+
Google Cloud project with Google Calendar API enabled
Supabase project with a meetings table
Google Gemini API key
credentials.json from Google Cloud Console

Installation

Clone the Repository:
git clone https://github.com/your-username/agentic-meeting-scheduler.git
cd agentic-meeting-scheduler


Set Up Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt

requirements.txt:
streamlit==1.10.0
google-generativeai==0.3.2
supabase==2.0.0
google-auth-oauthlib==1.0.0
google-api-python-client==2.90.0
pytz==2023.3



Configuration
Google Calendar API

In Google Cloud Console:
Create a project and enable Google Calendar API.
Go to Credentials > Create Credentials > OAuth 2.0 Client IDs > Desktop app.
Download the JSON file as credentials.json and place it in the project root:agentic-meeting-scheduler/
├── agentic_chatbot.py
├── requirements.txt
├── credentials.json





Supabase

In your Supabase project (https://hvbzuubgxfobyfgchgpr.supabase.co):
Create a meetings table with:
event_id (text, primary key)
title (text)
start_time (text)
description (text)
attendees (jsonb)
agenda (text, nullable)


SQL command:CREATE TABLE meetings (
    event_id TEXT PRIMARY KEY,
    title TEXT,
    start_time TEXT,
    description TEXT,
    attendees JSONB,
    agenda TEXT
);




Verify Supabase credentials in agentic_chatbot.py:SUPABASE_URL = "https://hvbzuubgxfobyfgchgpr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2Ynp1dWJneGZvYnlmZ2NoZ3ByIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0MDEwMTIsImV4cCI6MjA2Mjk3NzAxMn0.YJA-rpFVVIaYjqCULSgvepGYyGynrIUF1pksjHAaJhI"



Google Gemini API

Obtain an API key from Google AI Studio.
Update GEMINI_API_KEY in agentic_chatbot.py:GEMINI_API_KEY = "your-gemini-api-key"



Usage

Run the App:
streamlit run agentic_chatbot.py


Open http://localhost:8501.
Authenticate with Google Calendar on first run to generate token.json.


Schedule a Meeting:

In the sidebar, enter:
Date (e.g., May 19, 2025)
Time (e.g., 00:00)
Timezone (e.g., Asia/Kolkata)
Title (e.g., Team Meeting)
Description (e.g., Discuss Q2 progress)
Agenda (e.g., 1. Project updates\n2. Budget review)
Attendees (e.g., maithiligeek@gmail.com, akyadav13398@gmail.com)


Click Propose Meeting.
In the chat, type “Confirm the meeting” to schedule.


Verify Meetings:

Google Calendar: Check the primary calendar at https://calendar.google.com.
Email: Look for invitations in attendees’ inboxes (check spam).
Supabase: Query the meetings table:SELECT * FROM meetings WHERE event_id = '[event_id]';


Chat History: Review Streamlit chat for event ID.



Example
Sidebar Input:

Date: May 19, 2025
Time: 00:00
Timezone: Asia/Kolkata
Title: Team Meeting
Description: Discuss Q2 progress
Agenda: 1. Project updates\n2. Budget review
Attendees: maithiligeek@gmail.com, akyadav13398@gmail.com

Chat Output:
You: Proposed meeting: Team Meeting on 2025-05-19 00:00 Asia/Kolkata with maithiligeek@gmail.com, akyadav13398@gmail.com
Bot: I’ve noted your proposed meeting titled “Team Meeting” on May 19, 2025, at 12:00 AM IST with attendees maithiligeek@gmail.com, akyadav13398@gmail.com. Description: Discuss Q2 progress. Agenda: 1. Project updates\n2. Budget review. Please confirm to schedule or let me know if you’d like to make changes.
You: Confirm the meeting
Bot: Meeting scheduled successfully! Event ID: [unique_id]. Check your Google Calendar and email for confirmation.

Google Calendar: Event description includes “Discuss Q2 progress\n\nAgenda: 1. Project updates\n2. Budget review”.
Supabase: Stores agenda as “1. Project updates\n2. Budget review”.
Troubleshooting

Meeting Not Visible:

Check the primary calendar in Agenda view.
Ensure Google Calendar timezone is Asia/Kolkata.
Delete token.json and re-authenticate with the correct account.


No Email Notifications:

Check spam/junk folders.
Verify attendee emails are valid Google Calendar accounts.
Attendees may need to accept invitations due to Google’s anti-spam policies.


Supabase Errors:

Confirm the meetings table includes the agenda column.
Check terminal logs for “Supabase insert failed”.


Gemini API Issues:

Replace the placeholder API key (AIzaSyACqjXQAfqP2NX3pcAwdbQ3XX_-Z_MJZqY).
If gemini-1.5-flash-001-tuning fails, try gemini-1.5-flash.



Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m 'Add your feature').
Push to the branch (git push origin feature/your-feature).
Open a pull request.

License
MIT License
Contact
For issues or suggestions, open an issue on GitHub or email [your-email@example.com].

Built with Streamlit, Google Gemini, Google Calendar API, and SupabaseDate: May 16, 2025

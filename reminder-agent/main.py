# #type: ignore
# from agents import AsyncOpenAI, Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
# from dotenv import load_dotenv
# import os
# import asyncio
# import sqlite3
# import schedule
# import time
# import datetime
# import requests
# import streamlit as st
# import threading
# import json

# load_dotenv()
# set_tracing_disabled(True)



# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# client = AsyncOpenAI(
#     api_key = GEMINI_API_KEY,
#     base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
# )
# agent = Agent(
#     name="reminder-agent",
#     instructions="""
#     You are a reminder agent. Parse user input to extract:
#     - Reminder message
#     - Date and time (ISO format: YYYY-MM-DDTHH:MM:SS)
#     - Email
#     If any detail is missing, use defaults: email='user@example.com', message='Reminder', date=next day at 9 AM.
#     Return a JSON object with keys: message, email, remind_at. Ensure the output is valid JSON wrapped in ```json\n...\n```.
#     Example input: "set reminder for June 2, 2025, at 5:25 PM for meeting to nurjamila1@gmail.com"
#     Example output: ```json\n{"message": "meeting", "email": "nurjamila1@gmail.com", "remind_at": "2025-06-02T17:25:00"}\n
#     """,
#     model=OpenAIChatCompletionsModel(
#         model="gemini-2.0-flash",
#         openai_client=client
#     )
# )

# MAILGUN_API_URL = "https://api.mailgun.net/v3/sandbox75dffadc3d0241488094dc9f83b1a7fc.mailgun.org/messages"
# MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
# MAILGUN_DOMAIN = "sandbox75dffadc3d0241488094dc9f83b1a7fc.mailgun.org"

# conn = sqlite3.connect("reminders.db")
# cursor = conn.cursor()
# cursor.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, email TEXT, remind_at TEXT)")
# conn.commit()

# async def parse_input(user_input):
#     """Parse user input using the agent."""
#     try:
#         response = await Runner.run(agent, user_input)
#         print(f"Raw response: {response.final_output}")  # Debug logging
#         return json.loads(response.final_output)
#     except json.JSONDecodeError as e:
#         print(f"JSON parse error: {e}. Response: {response.final_output}")
#         return {
#             "message": "Reminder",
#             "email": "user@example.com",
#             "remind_at": (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0).isoformat()
#         }
#     except Exception as e:
#         print(f"Error in parse_input: {e}")
#         raise

# def store_reminder(message, email, remind_at):
#     """Store reminder in SQLite."""
#     cursor.execute("INSERT INTO reminders (message, email, remind_at) VALUES (?, ?, ?)", (message, email, remind_at))
#     conn.commit()


# def send_email(email, message):
#     """Send email using Mailgun."""
#     try:
#         response = requests.post(
#             MAILGUN_API_URL,
#             auth=("api", MAILGUN_API_KEY),
#             data={
#                 "from": f"Reminder <reminder@{MAILGUN_DOMAIN}>",
#                 "to": email,
#                 "subject": "Reminder",
#                 "text": message
#             }
#         )
#         print(f"Email sent to {email}: {response.status_code}")
#     except Exception as e:
#         print(f"Email error: {e}")

# def check_reminders():
#     """Check and send due reminders."""
#     now = datetime.datetime.now().isoformat()
#     cursor.execute("SELECT id, message, email FROM reminders WHERE remind_at <= ?", (now,))
#     for reminder_id, message, email in cursor.fetchall():
#         send_email(email, message)
#         cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
#         conn.commit()
# def run_scheduler():
#     """Run scheduler in background."""
#     schedule.every(60).seconds.do(check_reminders)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# def main():
#     st.title("Public Reminder Agent")
#     with st.form("reminder_form"):
#         user_input = st.text_input("Enter reminder (e.g., 'set reminder for June 10, 2025, at 10 AM for meeting to user@example.com')")
#         consent = st.checkbox("I consent to receive email reminders")
#         if st.form_submit_button("Set Reminder") and consent and user_input:
#             try:
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 data = loop.run_until_complete(parse_input(user_input))
#                 store_reminder(
#                     data.get("message", "Reminder"),
#                     data.get("email", "user@example.com"),
#                     data.get("remind_at", (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0).isoformat())
#                 )
#                 st.success(f"Reminder set for {data.get('email')}")
#             except Exception as e:
#                 st.error(f"Error: {e}")

# if __name__ == "__main__":
#     threading.Thread(target=run_scheduler, daemon=True).start()
#     main()

#type: ignore
from agents import AsyncOpenAI, Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os
import asyncio
import sqlite3
import schedule
import time
import datetime
import requests
import streamlit as st
import threading
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
set_tracing_disabled(True)

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
agent = Agent(
    name="reminder-agent",
    instructions="""
    You are a reminder agent. Parse user input to extract:
    - Reminder message
    - Date and time (ISO format: YYYY-MM-DDTHH:MM:SS)
    - Email
    If any detail is missing, use defaults: email='user@example.com', message='Reminder', date=next day at 9 AM.
    Return a JSON object with keys: message, email, remind_at. Ensure the output is valid JSON wrapped in ```json\n...\n```.
    Example input: "set reminder for June 2, 2025, at 5:25 PM for meeting to nurjamila1@gmail.com"
    Example output: ```json\n{"message": "meeting", "email": "nurjamila1@gmail.com", "remind_at": "2025-06-02T17:25:00"}\n```
    """,
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=client
    )
)

# Mailgun configuration
MAILGUN_API_URL = "https://api.mailgun.net/v3/sandbox75dffadc3d0241488094dc9f83b1a7fc.mailgun.org/messages"
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = "sandbox75dffadc3d0241488094dc9f83b1a7fc.mailgun.org"

# Initialize SQLite database
conn = sqlite3.connect("reminders.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, email TEXT, remind_at TEXT)")
conn.commit()

async def parse_input(user_input):
    """Parse user input using the agent."""
    try:
        response = await Runner.run(agent, user_input)
        logging.info(f"Raw response: {response.final_output}")
        # Extract JSON from response (handling potential markdown formatting)
        raw_output = response.final_output.strip()
        if raw_output.startswith("```json") and raw_output.endswith("```"):
            raw_output = raw_output[7:-3].strip()
        return json.loads(raw_output)
    except json.JSONDecodeError as e:
        logging.error(f"JSON parse error: {e}. Response: {response.final_output}")
        return {
            "message": "Reminder",
            "email": "user@example.com",
            "remind_at": (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0).isoformat()
        }
    except Exception as e:
        logging.error(f"Error in parse_input: {e}")
        raise

def store_reminder(message, email, remind_at):
    """Store reminder in SQLite."""
    cursor.execute("INSERT INTO reminders (message, email, remind_at) VALUES (?, ?, ?)", (message, email, remind_at))
    conn.commit()
    logging.info(f"Stored reminder: {message} for {email} at {remind_at}")

def send_email(email, message):
    """Send email using Mailgun."""
    try:
        response = requests.post(
            MAILGUN_API_URL,
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Reminder <reminder@{MAILGUN_DOMAIN}>",
                "to": email,
                "subject": "Reminder",
                "text": message
            }
        )
        logging.info(f"Email sent to {email}: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Email error: {e}")

def check_reminders():
    """Check and send due reminders."""
    now = datetime.datetime.now().isoformat()
    cursor.execute("SELECT id, message, email FROM reminders WHERE remind_at <= ?", (now,))
    for reminder_id, message, email in cursor.fetchall():
        send_email(email, message)
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        logging.info(f"Sent and deleted reminder {reminder_id} for {email}")

def run_scheduler():
    """Run scheduler in background."""
    schedule.every(60).seconds.do(check_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    st.title("Public Reminder Agent")
    with st.form("reminder_form"):
        user_input = st.text_input(
            "Enter reminder",
            value="set reminder for June 2, 2025, at 5:25 PM for meeting to nurjamila1@gmail.com"
        )
        consent = st.checkbox("I consent to receive email reminders")
        if st.form_submit_button("Set Reminder") and consent and user_input:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                data = loop.run_until_complete(parse_input(user_input))
                store_reminder(
                    data.get("message", "Reminder"),
                    data.get("email", "user@example.com"),
                    data.get("remind_at", (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0).isoformat())
                )
                st.success(f"Reminder set for {data.get('email')} at {data.get('remind_at')}")
            except Exception as e:
                st.error(f"Error: {e}")
                logging.error(f"Streamlit error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    main()

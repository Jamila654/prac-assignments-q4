#type: ignore
from agents import AsyncOpenAI, Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os, asyncio, sqlite3, time, datetime, streamlit as st, threading, json

load_dotenv()
set_tracing_disabled(True)


client = AsyncOpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
agent = Agent(
    name="reminder-agent",
    instructions="""
    I'm your Reminder Agent, here to help you set reminders! For reminder requests, extract:
    - Message (words after 'for' until the end, ignoring 'to', emails, or extra text like 't')
    - Date and time (ISO format: YYYY-MM-DDTHH:MM:SS, PKT UTC+5, from formats like 'June 2, 2025, 5:25 PM' or '2 June 2025 17:25')
    If message or date/time is missing, return {"error": "Please provide complete reminder details"}. 
    For unrelated input (e.g., "What's the weather?"), return {"error": "I'm your Reminder Agent, here to set reminders!"}.
    Return valid JSON wrapped in ```json\n...\n``` with keys: message, remind_at, error (if applicable).
    Example input: "set reminder for June 2, 2025, at 5:25 PM for meeting"
    Example output: ```json\n{"message": "meeting", "remind_at": "2025-06-02T17:25:00"}\n```
    Unrelated input: "What's the weather?"
    Unrelated output: ```json\n{"error": "I'm your Reminder Agent, here to set reminders!"}\n```
    """,
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client)
)


conn = sqlite3.connect("reminders.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, remind_at TEXT)")
conn.commit()

async def parse_input(user_input):
    try:
        response = await Runner.run(agent, user_input)
        raw = response.final_output.strip()
        if raw.startswith("```json") and raw.endswith("```"):
            raw = raw[7:-3].strip()
        data = json.loads(raw)
        if not data.get("message") or not data.get("remind_at"):
            return {"error": "Please provide complete reminder details"}
        return data
    except:
        return {"error": "I'm your Reminder Agent, here to set reminders!"}

def store_reminder(message, remind_at):
    cursor.execute("INSERT INTO reminders (message, remind_at) VALUES (?, ?)", (message, remind_at))
    conn.commit()

def check_reminders():
    now = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=5))).isoformat()
    cursor.execute("SELECT id, message FROM reminders WHERE remind_at <= ?", (now,))
    for id, message in cursor.fetchall():
        print(f"REMINDER: {message}")
        cursor.execute("DELETE FROM reminders WHERE id = ?", (id,))
        conn.commit()

def run_scheduler():
    while True:
        check_reminders()
        time.sleep(60)

def main():
    st.title("Your Reminder Agent")
    st.subheader("Current Reminders")
    cursor.execute("SELECT id, message, remind_at FROM reminders")
    reminders = cursor.fetchall()
    if reminders:
        for row in reminders:
            col1, col2 = st.columns([3, 1])
            col1.write(f"ID: {row[0]} | {row[1]} | {row[2]}")
            if col2.button("Delete", key=f"del_{row[0]}"):
                cursor.execute("DELETE FROM reminders WHERE id = ?", (row[0],))
                conn.commit()
                st.rerun()
    else:
        st.text("No reminders set yet.")

    if st.button("Clear All Reminders"):
        cursor.execute("DROP TABLE reminders")
        cursor.execute("CREATE TABLE reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, remind_at TEXT)")
        conn.commit()
        st.rerun()

    with st.form("reminder_form"):
        user_input = st.text_input("Set a Reminder", help="E.g., set reminder for June 2, 2025, at 9:15 PM for meeting")
        if st.form_submit_button("Submit"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(parse_input(user_input))
            if "error" in data:
                st.error(data["error"])
            else:
                store_reminder(data["message"], data["remind_at"])
                st.success(f"Reminder set for {data['remind_at']}")
                st.rerun()

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    main()



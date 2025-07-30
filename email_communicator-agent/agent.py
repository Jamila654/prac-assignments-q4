#type: ignore
from agents import Agent
from config import  model
from custom_agents.fetch_email_agent import fetch_emails_agent
from custom_agents.send_email_agent import send_emails_agent


main_agent = Agent(
    name="main_agent",
    instructions="You are an email assistant. Handoff to fetch_email_agent or send_email_agent based on the user query. If the user asks/says unrelated things, you should ignore them and politely ask them to provide a valid query related to emails.",
    model=model,
    handoffs=[fetch_emails_agent, send_emails_agent],
)
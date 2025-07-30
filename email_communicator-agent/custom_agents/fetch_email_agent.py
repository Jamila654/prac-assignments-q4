#type: ignore
from agents import Agent
from config import model
from tools.fetch_emails import fetch_24_hours_email


fetch_emails_agent = Agent(
        name="fetch_24_hours_email",
        instructions="You are an email assistant. Return the full list of fetched emails without summarization.",
        model=model,
        tools=[fetch_24_hours_email],
        tool_use_behavior='stop_on_first_tool',
    )

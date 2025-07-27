#type: ignore
from agents import Agent, Runner,function_tool
from config import config, model



@function_tool()
async def fetch_24_hours_email(email: str) -> str:
    # Simulate fetching emails for the last 24 hours
    return f"Fetched emails for {email} in the last 24 hours."

@function_tool()
async def send_email(email: str, subject: str, body: str) -> str:
    # Simulate sending an email
    return f"Email sent to {email} with subject '{subject}' and body '{body}'."
async def main():
    main_agent = Agent(
        name="EmailAssistant",
        instructions="You are an email assistant. You can fetch emails and send new emails.",
        model=model,
        tools=[fetch_24_hours_email, send_email]
    )
    result = await Runner.run(starting_agent=main_agent, input="what is the capital of France?", run_config=config)
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
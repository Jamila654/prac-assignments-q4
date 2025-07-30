#type: ignore
from agents import Agent, Runner
from config import config, model
from tools.send_email import send_email

send_emails_agent = Agent(
        name="send_email_agent",
        instructions="You are an email assistant. Send an email with the provided details and return the raw tool output without modification or mock data.",
        model=model,
        tools=[send_email],
        tool_use_behavior='stop_on_first_tool',
    )

# print("Welcome to the Email Assistant!")
# from_email = input("Enter the sender Gmail address: ").strip()
# to_email = input("Enter the recipient email address: ").strip()
# subject = input("Enter the email subject: ").strip()
# body = input("Enter the email body: ").strip()

# result = await Runner.run(
#     starting_agent=send_emails_agent,
#     input=f"send_email from '{from_email}' to '{to_email}' with subject '{subject}' and body '{body}'",
#     run_config=config
# )
    
# print(result.final_output)
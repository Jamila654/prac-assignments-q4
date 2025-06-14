#type: ignore
import os
from agents import AsyncOpenAI,Agent,Runner,set_tracing_disabled,OpenAIChatCompletionsModel,function_tool
from dotenv import load_dotenv
import asyncio

set_tracing_disabled(True)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model=OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")

async def main():
    shopping_agent = Agent(
    name="Shopping Assistant",
    instructions="You assist users in finding products and making purchase decisions.",
    model=model
    )

    support_agent = Agent(
        name="Support Agent",
        instructions="You help users with post-purchase support and returns.",
        model=model
    )

    shopping_tool = shopping_agent.as_tool(tool_name="ShoppingTool", tool_description="Find products and make purchase decisions.")
    support_tool = support_agent.as_tool(tool_name="SupportTool", tool_description="Provide post-purchase support and returns.")

    triage_agent = Agent(
        name="Triage Agent",
        instructions="You route user queries to the appropriate department.",
        model=model,
        tools=[shopping_tool, support_tool]
    )
    
    result = await Runner.run(triage_agent, "I need help with a recent purchase.")
    print(result.final_output)
    


if __name__ == "__main__":
    asyncio.run(main())

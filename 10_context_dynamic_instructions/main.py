#type: ignore
import asyncio
import random
from typing import Literal
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, Runner, function_tool, RunContextWrapper
from dotenv import load_dotenv
import os

load_dotenv()
set_tracing_disabled(True)

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")

class CustomContext:
    def __init__(self, style: Literal["haiku", "pirate", "robot"]):
        self.style = style

def custom_instructions(run_context: RunContextWrapper[CustomContext], agent: Agent[CustomContext])-> str:
    context = run_context.context
    if context.style == "haiku":
        return "Write in the style of a haiku, with a 5-7-5 syllable structure."
    elif context.style == "pirate":
        return "Speak like a pirate, using nautical terms and slang."
    elif context.style == "robot":
        return "Use a robotic tone, with precise and logical language."

agent = Agent(
    name="chat-agent",
    model=model,
    instructions=custom_instructions,
)
    

async def main():
    choice: Literal["haiku", "pirate", "robot"] = random.choice(["haiku", "pirate", "robot"])
    context = CustomContext(style=choice)
    print(f"Using style: {choice}\n")

    user_message = "Tell me a joke."
    print(f"User: {user_message}")
    result = await Runner.run(agent, user_message, context=context)

    print(f"Assistant: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())

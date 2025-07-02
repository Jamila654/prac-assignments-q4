#type: ignore
import asyncio
from dataclasses import dataclass
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, Runner, function_tool, RunContextWrapper
from dotenv import load_dotenv
import os


load_dotenv()
set_tracing_disabled(True)


gemini_api_key = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")


@dataclass
class UserInfo:
    name: str
    age: int
    color: str


global_name = ""
global_age = 10
global_color = ""


@function_tool
async def get_user_info_with_context(wrapper: RunContextWrapper[UserInfo]) -> str:
    return f"Hello! My name is {wrapper.context.name}, I am {wrapper.context.age} years old, and my favorite color is {wrapper.context.color}."

@function_tool
async def get_user_info_no_context() -> str:
    return f"Hello! My name is {global_name}, I am {global_age} years old, and my favorite color is {global_color}."


async def run_with_context(name: str, age: int, color: str):
    print("\n=== With Context ===")
    user_info = UserInfo(name=name, age=age, color=color)
    
    agent = Agent[UserInfo](
        name="UserInfoAgent",
        instructions="Call the get_user_info_with_context tool to show user details.",
        tools=[get_user_info_with_context],
        model=model
    )
    
    try:
        result = await Runner.run(
            starting_agent=agent,
            input="show my details",
            context=user_info,
        )
        print("Result with context:")
        print(result.final_output)
    except Exception as e:
        print(f"Error: {e}")


async def run_without_context(name: str, age: int, color: str):
    print("\n=== Without Context ===")
    global global_name, global_age, global_color
    global_name = name
    global_age = age
    global_color = color
    
    agent = Agent(
        name="UserInfoAgentNoContext",
        # instructions="Call the get_user_info_no_context tool to show user details.",
        tools=[get_user_info_no_context],
        model=model
    )
    
    try:
        result = await Runner.run(
            starting_agent=agent,
            input="show my details",
        )
        print("Result without context:")
        print(result.final_output)
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print("=== User Input ===")
    user_name = input("Enter your name: ")
    try:
        user_age = int(input("Enter your age: "))
    except ValueError:
        print("Please enter a valid number for age:")
        return
    user_color = input("Enter your favorite color: ")
    
    await run_with_context(user_name, user_age, user_color)
    await run_without_context(user_name, user_age, user_color)

if __name__ == "__main__":
    asyncio.run(main())
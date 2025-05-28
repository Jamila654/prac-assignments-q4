#type: ignore
import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
import os


load_dotenv()
set_tracing_disabled(disabled=True)

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

async def main():
    agent = Agent(
        name="Translator Agent",
        instructions="An agent that translates text from one language to another. If the user asks unrelated questions, respond with 'I am a translator agent, I can only translate text.'",
        model=OpenAIChatCompletionsModel(model="mistralai/devstral-small:free",openai_client=client,),
    )
    print("Translator Agent is ready. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit" or user_input.lower() == "quit":
            break

        result = await Runner.run(
            agent,
            user_input,
        )
        print(f"Assistant: {result.final_output}")




asyncio.run(main())

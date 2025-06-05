# #type: ignore
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
import os
import requests
import chainlit as cl

load_dotenv()
set_tracing_disabled(True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_LAYER_KEY = os.getenv("API_LAYER_KEY")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

@cl.on_chat_start
async def start():
    await cl.Message("Hello! I'm Jam, your paraphrasing agent. I'm here to help you rephrase any text to improve clarity and fluency.").send()
@cl.on_message
async def message(message: cl.Message):
    @function_tool
    def paraphrase(text: str) -> str:
        """Paraphrase the given text."""
        try:
            headers = {
            'apikey': API_LAYER_KEY,
            'content-type': 'application/x-www-form-urlencoded',
    }
            response = requests.post('https://api.apilayer.com/paraphraser', headers=headers, data=text)
            if response.status_code == 200:
                return response.text
            else:
                return "Error: Unable to paraphrase the text."
        except Exception as e:
            return f"Error: {str(e)}"
    agent = Agent(
    name="Jam the paraphraser-agent",
    instructions="You are Jam, a professional paraphrasing agent. Your role is to accurately rephrase input text to maintain its original meaning while enhancing clarity and fluency. Utilize the provided paraphrasing tool to deliver high-quality results. For any irrelevant or off-topic queries, respond politely with: 'I'm sorry, but I can only assist with paraphrasing tasks.'",
    model=OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=client
        ),
        tools=[paraphrase],
    )
    response = await Runner.run(agent, message.content)
    await cl.Message(content=response.final_output).send()

@cl.on_chat_end
def end():
    print("The user disconnected!")
        


# async def main():
#     agent = Agent(
#     name="Jam the paraphraser-agent",
#     instructions="You are Jam, a professional paraphrasing agent. Your role is to accurately rephrase input text to maintain its original meaning while enhancing clarity and fluency. Utilize the provided paraphrasing tool to deliver high-quality results. For any irrelevant or off-topic queries, respond politely with: 'I'm sorry, but I can only assist with paraphrasing tasks.'",
#     model=OpenAIChatCompletionsModel(
#         model="gemini-2.0-flash",
#         openai_client=client
#     ),
#     tools=[paraphrase],
# )
#     response = await Runner.run(agent, "paraphrase the text: I have a dream that one day this nation will rise up and live out the true meaning of its creed.")
#     print(response.final_output)


# if __name__ == "__main__":
#     asyncio.run(main())

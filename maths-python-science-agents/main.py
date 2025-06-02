#type: ignore
import asyncio
from agents import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
import os
import chainlit as cl


load_dotenv()
set_tracing_disabled(True)

MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    
)
MATHS_INSTRUCTIONS ="""
you are a maths agent your job is to answer user's maths related questions.If the user asks science related questions call the science agent.
if the user asks unrelated questions say "I am a maths agent, I can only answer maths related questions. If you have a science question, please ask the science agent.if the user says bye say "good bye" and end the chat.
"""
SCIENCE_INSTRUCTIONS = """
you are a science agent your job is to answer user's science related questions. If the user asks maths related questions call the maths agent.
if the user asks unrelated questions say "I am a science agent, I can only answer science related questions. If you have a maths question, please ask the maths agent. If the user says bye say "good bye" and end the chat.
"""

@cl.on_chat_start
async def start():
    await cl.Message(content='Science and Maths Agents are ready to answer your questions. type maths or science').send()

@cl.on_message
async def main(message: cl.Message):
    try:
        agent2 = Agent(
            name="Maths Agent",
            instructions=MATHS_INSTRUCTIONS,
            model=OpenAIChatCompletionsModel(
                model=MODEL,
                openai_client=client,
            )
        )
        agent = Agent(
            name="Science Agent",
            instructions=SCIENCE_INSTRUCTIONS,
            model=OpenAIChatCompletionsModel(
                model=MODEL,
                openai_client=client,
            ),
            handoffs=[agent2],
        )
        final_answer = Runner.run_sync(agent, message.content)
        await cl.Message(content=final_answer.final_output).send()
    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()

@cl.on_chat_end
def end():
    cl.Message(content="Chat ended").send()
    print("Chat ended")

# async def main():
#     agent2 = Agent(
#         name="Maths Agent",
#         instructions=MATHS_INSTRUCTIONS,
#         model=OpenAIChatCompletionsModel(
#             model=MODEL,
#             openai_client=client,
#         )
#     )
#     agent = Agent(
#         name="Science Agent",
#         instructions=SCIENCE_INSTRUCTIONS,
#         model=OpenAIChatCompletionsModel(
#             model=MODEL,
#             openai_client=client,
#         ),
#         handoffs=[agent2],
#     )
#     print("Agents are ready to answer your questionsType 'exit' to quit.")
#     while True:
#         user_input = input("Enter your question: ")
#         if user_input.lower() == "exit":
#             break
#         else:
#             final_answer = await Runner.run(agent, user_input)
#             print(final_answer.final_output)
    
# if __name__ == "__main__":
#     asyncio.run(main())


#type: ignore
from agents import set_tracing_disabled, Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel
import asyncio
from dotenv import load_dotenv
import os
import chainlit as cl

load_dotenv()
set_tracing_disabled(True)

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")


# async def main():
#     spanish_agent = Agent(
#         name="spanish agent",
#         instructions="You translate the user's message to Spanish",
#         model=model,
#         handoff_description="An english to spanish translator"
#     )
#     french_agent = Agent(
#         name="french agent",
#         instructions="You translate the user's message to French",
#         model=model,
#         handoff_description="An english to french translator"
#     )
#     italian_agent = Agent(
#         name="italian agent",
#         instructions="You translate the user's message to Italian",
#         model=model,
#         handoff_description="An english to italian translator"
#     )
#     spanish_agent = spanish_agent.as_tool(tool_name="spanish_agent",tool_description="An english to spanish translator")
#     french_agent = french_agent.as_tool(tool_name="french_agent", tool_description="An english to french translator")
#     italian_agent = italian_agent.as_tool(tool_name="italian_agent", tool_description="An english to italian translator")
    
#     orchestrator_agent = Agent(
#         name="orchestrator_agent",
#         instructions="""
#         You are a translation agent. You use the tools given to you to translate.
#         If asked for multiple translations, you call the relevant tools in order.
#         You never translate on your own, you always use the provided tools.
#         """,
#         model=model,
#         tools=[spanish_agent, french_agent, italian_agent]
#     )
#     print("welcome to the translation agent. I can translate english to spanish, french, and italian. What would you like to translate?")
#     result = await Runner.run(orchestrator_agent, "what is the meaning of life?")
#     print(result.final_output)


# if __name__ == "__main__":
#     asyncio.run(main())

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome to the translation agent. I can translate english to spanish, french, and italian. What would you like to translate?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Processing...")
    await msg.send()
    try:
        spanish_agent = Agent(
        name="spanish agent",
        instructions="You translate the user's message to Spanish",
        model=model,
        handoff_description="An english to spanish translator"
    )
        french_agent = Agent(
            name="french agent",
            instructions="You translate the user's message to French",
            model=model,
            handoff_description="An english to french translator"
        )
        italian_agent = Agent(
            name="italian agent",
            instructions="You translate the user's message to Italian",
            model=model,
            handoff_description="An english to italian translator"
        )
        spanish_agent = spanish_agent.as_tool(tool_name="spanish_agent",tool_description="An english to spanish translator")
        french_agent = french_agent.as_tool(tool_name="french_agent", tool_description="An english to french translator")
        italian_agent = italian_agent.as_tool(tool_name="italian_agent", tool_description="An english to italian translator")
        
        orchestrator_agent = Agent(
            name="orchestrator_agent",
            instructions="""
            You are a translation agent. You use the tools given to you to translate.
            If asked for multiple translations, you call the relevant tools in order.
            You never translate on your own, you always use the provided tools.
            """,
            model=model,
            tools=[spanish_agent, french_agent, italian_agent]
        )
        result = await Runner.run(orchestrator_agent, message.content)
        msg.content = result.final_output
        await msg.update()
        print(result.final_output)
    except Exception as e:
        print(e)
        msg.content = f"Error: {e}"
        await msg.update()
        return
    

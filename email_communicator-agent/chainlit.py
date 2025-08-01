#type: ignore
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner, ItemHelpers
from main import config
from agent import main_agent

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Hello, I'm an email assistant!").send()

@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()

    try:
        result = Runner.run_streamed(main_agent, input=message.content, run_config=config)

        final_output = ""

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                delta = event.data.delta
                final_output += delta
                await msg.stream_token(delta)
            elif event.type == "agent_updated_stream_event":
                print(f"[Agent updated] → {event.new_agent.name}")
                await cl.Message(content=f"Agent updated: {event.new_agent.name}").send()
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print(f"[Tool call] → {event.item.raw_item.name}")
                    await cl.Message(content=f"🎲 Tool decided: {event.item.raw_item.name}").send()
                elif event.item.type == "tool_call_output_item":
                    print(f"[Tool output] → {event.item.output}")
                    await cl.Message(content=f"🎲 Tool decided: {event.item.output}!").send()
                elif event.item.type == "message_output_item":
                    print(f"[Message output] → {ItemHelpers.text_message_output(event.item)}")

        msg.content = final_output
        await msg.update()

    except Exception as e:
        msg.content = f"❌ Error: {e}"
        await msg.update()

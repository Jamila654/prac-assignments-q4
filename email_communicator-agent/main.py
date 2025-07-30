#type: ignore
from agents import Runner,ItemHelpers
from openai.types.responses import ResponseTextDeltaEvent
from config import config
from agent import main_agent


async def main():
    print("Welcome to the Email Assistant!\n")
    user_input = input("Enter your query: ").strip()
    print("\nAgent output:\n")
    try:
        result = Runner.run_streamed(starting_agent=main_agent, input=user_input, run_config=config)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
                continue
            elif event.type == "agent_updated_stream_event":
                print(f"Agent updated: {event.new_agent.name}\n")
                continue
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print(f"Tool call: {event.item.raw_item.name}\n")
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}\n")
                elif event.item.type == "message_output_item":
                    print(f"\n\n-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                else:
                    pass  # Ignore other event types
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
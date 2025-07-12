# #type: ignore
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from agent import chat_agent
# from context import Message, Response
# from config import config
# from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, ItemHelpers
# import uvicorn
# from typing import Optional
# import json


# app = FastAPI(
#     title="FastAPI Streaming Chat Agent",
#     description="This is a streaming chat agent built with FastAPI.",
#     version='0.1.0'
# )
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# @app.get("/")
# async def root():
#     return {"message": "This is a streaming chat agent built with FastAPI."}

# @app.get("/users/{user_id}")
# async def get_user(user_id: str, role: Optional[str] = None):
#     user_info = {"user_id": user_id, "role": role if role else "guest"}
#     return user_info


# async def chat(message: Message):
#     if not message.text.strip():
#         raise HTTPException(status_code=400, detail="Message text cannot be empty")
#     try:
#         result = Runner.run_streamed(chat_agent, input=message.text, run_config=config)
#         async for event in result.stream_events():
#             if event.type == "raw_response_event":
#                 continue
#             elif event.type == "agent_updated_stream_event":
#                 chunk = json.dumps({"chunk": event.new_agent.name})
#                 yield f"Agent updated: {chunk}\n"
#                 print(f"Agent updated: {event.new_agent.name}")
#                 continue
#             elif event.type == "run_item_stream_event":
#                 if event.item.type == "tool_call_item":
#                     tool_name = event.item.raw_item.name  # Access the tool name from raw_item
#                     yield f"Tool was called: {tool_name}\n"  # Output: Tool was called: WebSearchAgent
#                     print(f"Tool was called: {tool_name}")
#                 elif event.item.type == "tool_call_output_item":
#                     chunk = json.dumps({"chunk": event.item.output})
#                     yield f"-- Tool output: {chunk}\n"
#                     print(f"-- Tool output: {event.item.output}")
#                 elif event.item.type == "message_output_item":
#                     chunk = json.dumps({"chunk": ItemHelpers.text_message_output(event.item)})
#                     yield f"-- Message output: {chunk}\n"
#                     print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
#                 else:
#                     pass
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")
    
#     except InputGuardrailTripwireTriggered as e:
#         reason = e.guardrail_result
#         error_msg = f"❌ Input rejected: {reason}"
#         print(error_msg)
    
#     except OutputGuardrailTripwireTriggered as e:
#         reason = e.guardrail_result.output_info.reasoning
#         error_msg = f"⚠️ Output blocked: {reason}"
#         print(error_msg)

# @app.post("/chat/", response_model=Response)
# async def chat_stream(message: Message):
#     if not message.text.strip():
#         raise HTTPException(
#             status_code=400, detail="Message text cannot be empty")
        
#     return StreamingResponse(
#         chat(message),
#         media_type="text/event-stream"
#         )

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

#type: ignore
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from agent import chat_agent
from context import Message, Response
from config import config
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, ItemHelpers
import uvicorn
from typing import Optional
import json
from openai.types.responses import ResponseTextDeltaEvent  # Assuming this import is needed for delta events


app = FastAPI(
    title="FastAPI Streaming Chat Agent",
    description="This is a streaming chat agent built with FastAPI.",
    version='0.1.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "This is a streaming chat agent built with FastAPI."}

@app.get("/users/{user_id}")
async def get_user(user_id: str, role: Optional[str] = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info


async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    try:
        result = Runner.run_streamed(chat_agent, input=message.text, run_config=config)
        
        async for event in result.stream_events():
            # Stream incremental text from raw_response_event with ResponseTextDeltaEvent
            if event.type == "raw_response_event":
                if hasattr(event, "data") and isinstance(event.data, ResponseTextDeltaEvent):
                    if hasattr(event.data, 'delta') and event.data.delta:
                        chunk = json.dumps({"chunk": event.data.delta})
                        yield f"data: {chunk}\n\n"
                        asyncio.sleep(1)
                        continue
            
            # Agent updated event
            elif event.type == "agent_updated_stream_event":
                if hasattr(event, "new_agent") and hasattr(event.new_agent, "name"):
                    chunk = json.dumps({"agent_updated": event.new_agent.name})
                    yield f"data: {chunk}\n\n"
                    print(f"Agent updated: {event.new_agent.name}")
                    continue
            
            # Tool call and output events
            elif event.type == "run_item_stream_event":
                if hasattr(event, "item") and event.item:
                    if event.item.type == "tool_call_item":
                        tool_name = getattr(event.item.raw_item, "name", "Unknown Tool")
                        chunk = json.dumps({"tool_called": tool_name})
                        yield f"data: {chunk}\n\n"
                        print(f"Tool was called: {tool_name}")
                    elif event.item.type == "tool_call_output_item":
                        output = event.item.output if hasattr(event.item, "output") else ""
                        chunk = json.dumps({"tool_output": output})
                        yield f"data: {chunk}\n\n"
                        print(f"Tool output: {output}")
                    elif event.item.type == "message_output_item":
                        text_output = ItemHelpers.text_message_output(event.item)
                        chunk = json.dumps({"message_output": text_output})
                        yield f"data: {chunk}\n\n"
                        print(f"Message output:\n{text_output}")
                    else:
                        # For other item types, optionally handle or skip
                        pass
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")
    
    except InputGuardrailTripwireTriggered as e:
        reason = e.guardrail_result
        error_msg = f"❌ Input rejected: {reason}"
        print(error_msg)
    
    except OutputGuardrailTripwireTriggered as e:
        reason = e.guardrail_result.output_info.reasoning
        error_msg = f"⚠️ Output blocked: {reason}"
        print(error_msg)


@app.post("/chat/", response_model=Response)
async def chat_stream(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")
        
    return StreamingResponse(
        chat(message),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

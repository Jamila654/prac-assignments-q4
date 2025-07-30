#type: ignore
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config import config
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, ItemHelpers
import uvicorn
import json
from openai.types.responses import ResponseTextDeltaEvent
from agent import main_agent

app = FastAPI(
    title="FastAPI Streaming Chat Agent",
    description="This is a streaming chat agent built with FastAPI.",
    version='0.1.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://prac-assignments-q4-six.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Email Assistant! Send a POST request to /chat/ with your message."}



async def chat(message: str):
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    try:
        result = Runner.run_streamed(main_agent, input=message, run_config=config)

        async for event in result.stream_events():
            # Stream incremental text from raw_response_event with ResponseTextDeltaEvent
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    chunk = json.dumps({"chunk": event.data.delta})
                    yield f"data: {chunk}\n\n"
                    continue
            
            # Agent updated event
            elif event.type == "agent_updated_stream_event":
                    chunk = json.dumps({"agent_updated": event.new_agent.name})
                    yield f"data: {chunk}\n\n"
                    print(f"Agent updated: {event.new_agent.name}")
                    continue
            
            # Tool call and output events
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                        chunk = json.dumps({"tool_called": event.item.raw_item.name})
                        yield f"data: {chunk}\n\n"
                        print(f"Tool was called: {event.item.raw_item.name}")
                elif event.item.type == "tool_call_output_item":
                        chunk = json.dumps({"tool_output": event.item.output})
                        yield f"data: {chunk}\n\n"
                        print(f"-- Tool output: {event.item.output}\n")
                elif event.item.type == "message_output_item":
                        text_output = ItemHelpers.text_message_output(event.item)
                        chunk = json.dumps({"message_output": text_output})
                        yield f"data: {chunk}\n\n"
                        print(f"Message output:\n{text_output}")
                else:    # For other item types, optionally handle or skip
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


@app.post("/chat/")
async def chat_stream(message: str):
    if not message.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")
        
    return StreamingResponse(
        chat(message),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

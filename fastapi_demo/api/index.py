from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import UTC, datetime
from uuid import uuid4
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from typing import cast
import os

# Remove load_dotenv() - Vercel handles environment variables differently
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=cast(ModelProvider, external_client),
    tracing_disabled=True
)

app = FastAPI(
    title="FastAPI Demo",
    description="A simple FastAPI application with an agent and a runner.",
    version='0.1.0'
)

class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] | None = None

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool.",
    tools=[get_current_time],
    model=model,
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API!"}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

@app.post("/api/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    
    try:
        # Use the OpenAI Agents SDK to process the message
        result = await Runner.run(chat_agent, input=message.text, run_config=config)
        reply_text = result.final_output
        
        return Response(
            user_id=message.user_id,
            reply=reply_text,
            metadata=Metadata()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

# Remove the uvicorn.run() call - not needed for Vercel

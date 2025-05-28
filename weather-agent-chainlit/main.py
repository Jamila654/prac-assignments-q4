#type: ignore
from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
import requests
import os
import chainlit as cl
from typing import Dict, Optional


load_dotenv()

set_tracing_disabled(disabled=True)

MODEL = 'gemini/gemini-2.0-flash'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENWEATHER_API_KEY= os.getenv('OPENWEATHER_API_KEY')
github_client_id = os.getenv("OAUTH_GITHUB_CLIENT_ID")
github_client_secret = os.getenv("OAUTH_GITHUB_CLIENT_SECRET")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user

@cl.on_chat_start
async def on_chat_start():
    await cl.Message("Hello, I am a weather agent. How can I help you?").send()
    

@cl.on_message
async def on_message(message: cl.Message):
    try:
        @function_tool
        def get_weather(city: str) -> str:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(data)
                weather = data['weather'][0]['description']
                temperature = data['main']['temp']
                feels_like = data['main']['feels_like']
                return f"The weather in {city} is {weather} with a temperature of {temperature}°C and a feels like temperature of {feels_like}°C."
            else:
                return f"Error: Unable to get weather for {city}. Please try again later."
        agent = Agent(
            name='Weather Agent',
            instructions='You are a Weather Agent tasked with providing accurate weather information for a specified city using the provided get_weather tool. When a user requests the weather, use the tool to fetch and return the current weather conditions, including description, temperature, and feels-like temperature in Celsius. If the city is not found or an error occurs, respond with: "Could not get weather for [city]. Please check the city name." For non-weather-related queries, respond: "I am a Weather Agent and can only provide weather information for a city." If the user says "bye," "goodbye," "exit," or "quit," respond with: "Thank you for using the Weather Agent. Goodbye." and terminate the interaction.',
            model=LitellmModel(MODEL, api_key=GEMINI_API_KEY),
            tools=[get_weather],
       )
        final_answer = Runner.run_sync(agent, message.content)
        await cl.Message(final_answer.final_output).send()
    except Exception as e:
        print(e)
        await cl.Message(e).send()
        return

@cl.on_chat_end
def on_chat_end():
    print("Chat ended")
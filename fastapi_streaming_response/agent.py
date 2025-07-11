#type: ignore
from agents import Agent
from config import model
from guardrails import input_climate_guardrail, output_climate_guardrail


web_search_agent = Agent(
    name="WebSearchAgent",
    instructions="Perform web searches and return relevant content for climate-related queries.",
    model=model,

)
web_search_agent_as_tool = web_search_agent.as_tool(
    tool_name="WebSearchAgent",
    tool_description="Performs web searches for climate-related information.",
)

chat_agent = Agent(
    name="Streaming Chat Agent🤖",
    instructions="You are a specialized climate reporting agent. Strictly handle only climate-related topics. Use 'WebSearchAgent' for climate information gathering",
    model=model,
    tools=[web_search_agent_as_tool],
    input_guardrails=[input_climate_guardrail],
    output_guardrails=[output_climate_guardrail],
)
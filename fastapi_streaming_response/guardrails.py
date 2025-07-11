#type: ignore
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
)
from config import model, config

class ClimateCheck(BaseModel):
    is_climate_related: bool
    reasoning: str


input_guardrail_agent = Agent(
    name="InputClimateGuard",
    instructions="Check if the user request is related to climate change or environmental topics. Return true only for climate topics.",
    output_type=ClimateCheck,
    model=model
)

@input_guardrail
async def input_climate_guardrail(
    ctx: RunContextWrapper, agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    # Extract last user message
    user_input = input[-1]["content"] if isinstance(input, list) else input
    
    result = await Runner.run(input_guardrail_agent, user_input)
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_climate_related
    )
    
output_guardrail_agent = Agent(
    name="OutputClimateGuard",
    instructions="Verify if the generated content is about climate change or environmental topics. if not, return false.",
    output_type=ClimateCheck,
    model=model
)

@output_guardrail
async def output_climate_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, output)
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_climate_related
    )

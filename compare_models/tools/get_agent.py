from strands.models import BedrockModel
from strands import Agent
from strands_tools import calculator
import os

agent = None

def get_agent(system_prompt, model_id=None):
    global agent
    if agent is None:
        if model_id is None:
            model_id = os.getenv("MODEL_ID", "eu.anthropic.claude-3-7-sonnet-20250219-v1:0")
        model = BedrockModel(
            model_id=model_id,
            region_name=os.getenv("AWS_REGION", "eu-central-1"),
            max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
            temperature=float(os.getenv("TEMPERATURE", "0.3")),
            top_p=float(os.getenv("TOP_P", "0.8")),
        )
        agent = Agent(
            model=model,
            system_prompt=system_prompt,
            tools=[calculator]
        )
    return agent
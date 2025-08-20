from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

from tools.get_agent import get_agent

agent = None

def load_system_prompt():
    with open("system_prompt.txt", "r") as f:
        return f.read().strip()

@app.entrypoint
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    system_prompt = payload.get("system_prompt", load_system_prompt())
    model_id = payload.get("model_id")
    agent = get_agent(system_prompt, model_id)
    user_input = payload.get("prompt")
    print("User input:", user_input)
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run(port=8081)
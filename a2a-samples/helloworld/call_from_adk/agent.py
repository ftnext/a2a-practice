from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

root_agent = RemoteA2aAgent(
    name="Parrot_Agent", agent_card="http://0.0.0.0:9999/.well-known/agent.json"
)

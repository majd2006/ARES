from app.agents.network_agent import NetworkIntelligenceAgent


agent = NetworkIntelligenceAgent()

phone_number = "+99999991000"

location = agent.get_responder_location(phone_number)

print("ARES Network Intelligence Agent")
print("Responder location:")
print(location)
from app.agents.network_agent import NetworkIntelligenceAgent


agent = NetworkIntelligenceAgent()

result = agent.check_responder_reachability("+99999991000")

print("ARES Network Intelligence Agent")
print(result)

if result["reachable"]:
    print("Decision: responder can remain a deployment candidate.")
else:
    print("Decision: responder should be deprioritized or excluded.")
from app.agents.resource_escalation_agent import (
    ResourceEscalationAgent,
)

from app.agents.response_planning_agent import (
    ResponsePlanningAgent,
)

from app.optimization.responder_ranker import (
    ResponderRanker,
)

from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
    disaster_zones,
)


zone = disaster_zones[0]

ranker = ResponderRanker()
planner = ResponsePlanningAgent()
escalation_agent = ResourceEscalationAgent()


ranked_responders = ranker.rank_responders(
    responders=responder_teams,
    disaster_zone=zone,
)


plan = planner.generate_plan(
    disaster_zone=zone,
    responders=ranked_responders,
    hospitals=hospitals,
    relief_centers=relief_centers,
)


escalation = escalation_agent.evaluate(
    response_plan=plan,
    hospitals=hospitals,
    relief_centers=relief_centers,
)


print("ARES RESOURCE ESCALATION")
print("========================")

print()
print(
    "Status:",
    escalation["status"].upper(),
)

print()
print("Alerts")
print("------")

for alert in escalation["alerts"]:
    print()
    print(
        f"[{alert['severity'].upper()}] "
        f"{alert['message']}"
    )

print()
print("Reinforcement Requests")
print("----------------------")

for request in escalation[
    "reinforcement_requests"
]:
    print()
    print(
        f"{request['resource_type']}: "
        f"{request['required_quantity']}"
    )
    print(
        f"Priority: "
        f"{request['priority'].upper()}"
    )
    print(
        request["action"]
    )
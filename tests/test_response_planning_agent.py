from app.agents.response_planning_agent import (
    ResponsePlanningAgent,
)
from app.optimization.responder_ranker import ResponderRanker
from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
    disaster_zones,
)


ranker = ResponderRanker()
planner = ResponsePlanningAgent()

zone = disaster_zones[0]

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


print("ARES RESPONSE PLAN")
print("------------------")

print(f"\nIncident: {plan['zone_name']}")
print(f"Severity: {plan['severity'].upper()}")

resources = plan["recommended_resources"]

print("\nRecommended Resources")
print(f"Medical teams: {resources['medical_teams']}")
print(f"Ambulances: {resources['ambulances']}")
print(f"Volunteers: {resources['volunteers']}")

print("\nResponder Assignments")

for assignment in plan["responder_assignments"]:
    print(
        f"{assignment['priority']}. "
        f"{assignment['name']} -> "
        f"{assignment['mission']}"
    )

print("\nHospital Allocation")

for allocation in plan["hospital_allocations"]:
    print(
        f"{allocation['hospital_name']}: "
        f"{allocation['allocated_critical_patients']} "
        f"critical patients"
    )

print("\nReserve Resources")

reserve = plan["reserve_resources"]

print(f"Medical teams: {reserve['medical_teams']}")
print(f"Ambulances: {reserve['ambulances']}")
print(f"Volunteers: {reserve['volunteers']}")

if plan["unallocated_critical_patients"] > 0:
    print(
        "\nWARNING: "
        f"{plan['unallocated_critical_patients']} "
        "critical patients exceed available hospital capacity."
    )
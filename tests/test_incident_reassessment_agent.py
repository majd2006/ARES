from app.agents.incident_reassessment_agent import (
    IncidentReassessmentAgent,
)


agent = IncidentReassessmentAgent()


previous_incident = {
    "affected_radius_km": 0.5,
    "estimated_population": 2198,
    "estimated_casualties": 494,
    "estimated_critical": 120,
    "severity": "critical",
}


current_incident = {
    "affected_radius_km": 0.7,
    "estimated_population": 4926,
    "estimated_casualties": 1107,
    "estimated_critical": 270,
    "severity": "critical",
}


result = agent.compare(
    previous_incident=previous_incident,
    current_incident=current_incident,
)


print("ARES INCIDENT REASSESSMENT")
print("==========================")

print()
print(
    "Status:",
    result["status"].upper(),
)

print(
    "Replanning required:",
    result["requires_replanning"],
)

print(
    "Detected changes:",
    result["change_count"],
)

print()
print("Changes")
print("-------")


for change in result["changes"]:

    print()

    print(
        f"[{change['severity'].upper()}]"
    )

    print(
        change["message"]
    )
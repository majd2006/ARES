from pprint import pprint

from app.orchestration.ares_orchestrator import (
    ARESOrchestrator,
)

from app.agents.incident_ingestion_agent import (
    IncidentInput,
)

from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
)


def main():

    incident = IncidentInput(
        incident_id="V2-TEST-001",
        source="prototype_v2_test",
        timestamp="2026-08-31T00:00:00Z",

        latitude=47.490,
        longitude=19.080,

        disaster_type="explosion",
        severity="critical",

        affected_radius_km=0.5,
        population_density_per_km2=2800,

        description=(
            "ARES V2 orchestration test."
        ),
    )

    orchestrator = ARESOrchestrator()

    result = orchestrator.run_incident(
        incident=incident,
        responders=responder_teams,
        hospitals=hospitals,
        relief_centers=relief_centers,
    )

    print("\n")
    print("=" * 70)
    print("ARES V2 ORCHESTRATION RESULT")
    print("=" * 70)

    print("\nORCHESTRATION")
    pprint(
        result["orchestration"]
    )

    print("\nASSESSMENT")
    pprint(
        result["assessment"]
    )

    print("\nRESPONDER DECISIONS")

    for responder in result["responders"]:

        print(
            responder["team_id"],
            responder["name"],
            "| reachable:",
            responder["reachable"],
            "| eligible:",
            responder[
                "eligible_for_deployment"
            ],
            "| distance:",
            responder[
                "distance_to_disaster_km"
            ],
            "km",
        )

    print("\nRESPONSE PLAN")
    pprint(
        result["response_plan"]
    )

    print("\nOPERATIONAL STRATEGY")

    for action in (
        result[
            "operational_strategy"
        ]["actions"]
    ):

        print(
            f"{action['priority']}. "
            f"[{action['category']}] "
            f"{action['title']}"
        )

    print("\n")
    print("=" * 70)
    print("ARES V2 PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
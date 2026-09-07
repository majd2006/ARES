from pprint import pprint

from app.agents.incident_ingestion_agent import (
    IncidentInput,
    IncidentIngestionAgent,
)

from app.orchestration.ares_orchestrator import (
    ARESOrchestrator,
)

from data.beirut_demo_scenario import (
    beirut_responder_teams,
    beirut_hospitals,
    beirut_relief_centers,
    BEIRUT_PORT_LATITUDE,
    BEIRUT_PORT_LONGITUDE,
)


def main():

    print()
    print("=" * 72)
    print("ARES — BEIRUT PORT HISTORICAL SCENARIO")
    print("=" * 72)

    # ======================================================
    # 1. HISTORICAL SCENARIO INPUT
    # ======================================================

    incident_input = IncidentInput(
        incident_id="BEIRUT-PORT-2020-DEMO",

        source="historical_demo_scenario",

        timestamp="2020-08-04T18:08:00+03:00",

        latitude=BEIRUT_PORT_LATITUDE,
        longitude=BEIRUT_PORT_LONGITUDE,

        disaster_type="explosion",
        severity="critical",

        affected_radius_km=0.5,

        # Demonstration population-density assumption.

        # This value is used only by the ARES prototype
        # assessment model and is not presented as a
        # historical measurement of Beirut on 4 August 2020.
        population_density_per_km2=2800,

        description=(
            "Historical simulation inspired by the "
            "4 August 2020 Beirut Port explosion. "
            "Operational resources and scenario inputs "
            "are simulated for demonstration."
        ),
    )

    # ======================================================
    # 2. NORMALIZE INCIDENT
    # ======================================================

    ingestion_agent = (
        IncidentIngestionAgent()
    )

    incident = (
        ingestion_agent.ingest(
            incident_input
        )
    )

    # ======================================================
    # 3. RUN ARES
    # ======================================================

    orchestrator = (
        ARESOrchestrator()
    )

    decision = (
        orchestrator.run_incident(
            incident=incident,

            responders=(
                beirut_responder_teams
            ),

            hospitals=(
                beirut_hospitals
            ),

            relief_centers=(
                beirut_relief_centers
            ),

            operational_location_mode=(
                "registered_scenario"
            ),
        )
    )

    # ======================================================
    # 4. OUTPUT
    # ======================================================

    print()
    print("INCIDENT")
    pprint(
        decision["incident"]
    )

    print()
    print("ASSESSMENT")
    pprint(
        decision["assessment"]
    )

    print()
    print("RESPONDER DECISIONS")

    for responder in decision["responders"]:

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
            "| location source:",
            responder["location_source"],
        )

    print()
    print("CAMARA DECISION TRACE")

    for event in (
        decision[
            "agentic_orchestration"
        ]["tool_trace"]
    ):

        print(
            event["team_id"],
            "|",
            event["tool"],
            "| invoked:",
            event["invoked"],
            "| result:",
            event["result"],
            "| success:",
            event.get(
                "success",
                "N/A",
            ),
        )

    print()
    print("CAMARA SUMMARY")

    print(
        "Actual CAMARA calls:",
        decision[
            "agentic_orchestration"
        ]["camara_calls"],
    )

    print(
        "Successful calls:",
        decision[
            "agentic_orchestration"
        ]["successful_calls"],
    )

    print(
        "Failed calls:",
        decision[
            "agentic_orchestration"
        ]["failed_calls"],
    )

    print()
    print("RESPONSE PLAN")

    pprint(
        decision["response_plan"]
    )

    print()
    print("OPERATIONAL STRATEGY")

    for action in (
        decision[
            "operational_strategy"
        ]["actions"]
    ):

        print(
            f"{action['priority']}. "
            f"[{action['category']}] "
            f"{action['title']}"
        )

        print(
            f"   {action['description']}"
        )

    print()
    print("=" * 72)
    print(
        "BEIRUT HISTORICAL SCENARIO COMPLETED"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
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

    # ======================================================
    # TEST INCIDENT
    # ======================================================

    incident = IncidentInput(
        incident_id="V2-TEST-001",

        source="prototype_v2_test",

        timestamp=(
            "2026-08-31T00:00:00Z"
        ),

        latitude=47.490,
        longitude=19.080,

        disaster_type="explosion",

        severity="critical",

        affected_radius_km=0.5,

        population_density_per_km2=2800,

        description=(
            "ARES V2 multi-API "
            "orchestration test."
        ),
    )

    # ======================================================
    # CREATE ORCHESTRATOR
    # ======================================================

    orchestrator = (
        ARESOrchestrator()
    )

    # ======================================================
    # RUN COMPLETE ARES PIPELINE
    # ======================================================

    result = (
        orchestrator.run_incident(
            incident=incident,

            responders=(
                responder_teams
            ),

            hospitals=hospitals,

            relief_centers=(
                relief_centers
            ),
        )
    )

    # ======================================================
    # HEADER
    # ======================================================

    print("\n")

    print("=" * 70)

    print(
        "ARES V2 ORCHESTRATION RESULT"
    )

    print("=" * 70)

    # ======================================================
    # ORCHESTRATION
    # ======================================================

    print(
        "\nORCHESTRATION"
    )

    pprint(
        result[
            "orchestration"
        ]
    )

    # ======================================================
    # DISASTER ASSESSMENT
    # ======================================================

    print(
        "\nASSESSMENT"
    )

    pprint(
        result[
            "assessment"
        ]
    )

    # ======================================================
    # RESPONDER DECISIONS
    # ======================================================

    print(
        "\nRESPONDER DECISIONS"
    )

    for responder in (
        result[
            "responders"
        ]
    ):

        print(
            responder["team_id"],
            responder["name"],

            "| reachable:",
            responder["reachable"],

            "| eligible:",
            responder["eligible_for_deployment"],

            "| lat:",
            responder["latitude"],

            "| lon:",
            responder["longitude"],

            "| distance:",
            responder["distance_to_disaster_km"],
            "km",

            "| location source:",
            responder.get(
                "location_source"
            ),

            "| degraded:",
            responder.get(
                "network_degraded"
            ),
        )

    # ======================================================
    # CAMARA ORCHESTRATION TRACE
    # ======================================================

    print(
        "\nCAMARA ORCHESTRATION TRACE"
    )

    for event in (
        result[
            "agentic_orchestration"
        ][
            "tool_trace"
        ]
    ):

        print(
            event[
                "team_id"
            ],

            "|",

            event[
                "tool"
            ],

            "| invoked:",

            event.get(
                "invoked"
            ),

            "| result:",

            event.get(
                "result"
            ),

            "| success:",

            event.get(
                "success",
                "N/A",
            ),

            "| duration:",

            event.get(
                "duration_ms",
                "N/A",
            ),

            "ms",
        )

        if event.get(
            "error"
        ):

            print(
                "   ERROR:",
                event[
                    "error"
                ],
            )

    # ======================================================
    # CAMARA SUMMARY
    # ======================================================

    orchestration = (
        result[
            "agentic_orchestration"
        ]
    )

    print(
        "\nCAMARA SUMMARY"
    )

    print(
        "Total CAMARA calls:",
        orchestration[
            "camara_calls"
        ],
    )

    print(
        "Successful calls:",
        orchestration[
            "successful_calls"
        ],
    )

    print(
        "Failed calls:",
        orchestration[
            "failed_calls"
        ],
    )

    # ======================================================
    # RESPONSE PLAN
    # ======================================================

    print(
        "\nRESPONSE PLAN"
    )

    pprint(
        result[
            "response_plan"
        ]
    )

    # ======================================================
    # OPERATIONAL STRATEGY
    # ======================================================

    print(
        "\nOPERATIONAL STRATEGY"
    )

    actions = (
        result[
            "operational_strategy"
        ][
            "actions"
        ]
    )

    for action in actions:

        print(
            f"{action['priority']}. "
            f"[{action['category']}] "
            f"{action['title']}"
        )

    # ======================================================
    # COMPLETION
    # ======================================================

    print("\n")

    print("=" * 70)

    print(
        "ARES V2 PIPELINE COMPLETED"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()
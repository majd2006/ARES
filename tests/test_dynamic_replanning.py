from app.orchestration.ares_orchestrator import (
    ARESOrchestrator,
)

from app.orchestration.decision_replanner import (
    DecisionReplanner,
)

from app.agents.incident_ingestion_agent import (
    IncidentInput,
)

from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
)


def print_assignments(
    title,
    decision,
):

    print(
        f"\n{title}"
    )

    assignments = (
        decision[
            "response_plan"
        ][
            "responder_assignments"
        ]
    )

    if not assignments:

        print(
            "No responder assignments."
        )

        return

    for assignment in assignments:

        print(
            assignment[
                "priority"
            ],

            "|",

            assignment[
                "team_id"
            ],

            assignment[
                "name"
            ],

            "|",

            assignment[
                "mission"
            ],
        )


def main():

    print("\n")

    print("=" * 72)

    print(
        "ARES V2 DYNAMIC REPLANNING TEST"
    )

    print("=" * 72)

    # ======================================================
    # INCIDENT
    # ======================================================

    incident = IncidentInput(
        incident_id=(
            "V2-REPLAN-001"
        ),

        source=(
            "dynamic_replanning_test"
        ),

        timestamp=(
            "2026-08-31T00:00:00Z"
        ),

        latitude=47.490,
        longitude=19.080,

        disaster_type=(
            "explosion"
        ),

        severity=(
            "critical"
        ),

        affected_radius_km=0.5,

        population_density_per_km2=(
            2800
        ),

        description=(
            "ARES dynamic responder "
            "replanning test."
        ),
    )

    orchestrator = (
        ARESOrchestrator()
    )

    replanner = (
        DecisionReplanner()
    )

    # ======================================================
    # DECISION 1 — BASELINE
    # ======================================================

    print(
        "\nGenerating baseline decision..."
    )

    previous_decision = (
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

    print_assignments(
        "BASELINE DEPLOYMENT",
        previous_decision,
    )

    # ======================================================
    # SELECT AN ACTIVE TEAM FOR OUTAGE
    # ======================================================

    assignments = (
        previous_decision[
            "response_plan"
        ][
            "responder_assignments"
        ]
    )

    if not assignments:

        raise RuntimeError(
            "No baseline responder "
            "was assigned."
        )

    outage_team_id = (
        assignments[0][
            "team_id"
        ]
    )

    outage_team_name = (
        assignments[0][
            "name"
        ]
    )

    print(
        "\nNETWORK EVENT"
    )

    print(
        outage_team_id,
        outage_team_name,
        "lost operational connectivity."
    )

    # ======================================================
    # DECISION 2 — NETWORK OUTAGE
    # ======================================================

    print(
        "\nGenerating revised decision..."
    )

    current_decision = (
        orchestrator.run_incident(
            incident=incident,

            responders=(
                responder_teams
            ),

            hospitals=hospitals,

            relief_centers=(
                relief_centers
            ),

            offline_team_ids={
                outage_team_id
            },
        )
    )

    print_assignments(
        "REVISED DEPLOYMENT",
        current_decision,
    )

    # ======================================================
    # DECISION COMPARISON
    # ======================================================

    replanning_result = (
        replanner.compare(
            previous_decision=(
                previous_decision
            ),

            current_decision=(
                current_decision
            ),

            trigger={
                "type":
                    "network_outage",

                "team_id":
                    outage_team_id,

                "team_name":
                    outage_team_name,

                "source":
                    "simulated_runtime_event",
            },
        )
    )

    # ======================================================
    # REPLANNING TRACE
    # ======================================================

    print(
        "\nARES REPLANNING TRACE"
    )

    print(
        "Status:",
        replanning_result[
            "status"
        ],
    )

    print(
        "Requires replanning:",
        replanning_result[
            "requires_replanning"
        ],
    )

    print(
        "Trigger:",
        replanning_result[
            "trigger"
        ][
            "type"
        ],
    )

    print(
        "Affected team:",
        outage_team_id,
        outage_team_name,
    )

    print(
        "Material changes:",
        replanning_result[
            "material_change_count"
        ],
    )

    # ======================================================
    # CHANGES
    # ======================================================

    print(
        "\nDECISION DELTA"
    )

    for index, change in enumerate(
        replanning_result[
            "changes"
        ],
        start=1,
    ):

        print(
            f"{index}.",
            f"[{change['type']}]",
            change[
                "message"
            ],
        )

    # ======================================================
    # VERIFY OUTAGE TEAM
    # ======================================================

    current_responder = next(
        responder
        for responder
        in current_decision[
            "responders"
        ]
        if responder[
            "team_id"
        ] == outage_team_id
    )

    print(
        "\nOUTAGE TEAM FINAL STATE"
    )

    print(
        "Team:",
        current_responder[
            "team_id"
        ],
        current_responder[
            "name"
        ],
    )

    print(
        "Reachable:",
        current_responder[
            "reachable"
        ],
    )

    print(
        "Eligible:",
        current_responder[
            "eligible_for_deployment"
        ],
    )

    print(
        "Runtime override:",
        current_responder[
            "runtime_network_override"
        ],
    )

    # ======================================================
    # FINAL
    # ======================================================

    print("\n")

    print("=" * 72)

    print(
        "ARES DYNAMIC REPLANNING TEST COMPLETED"
    )

    print("=" * 72)


if __name__ == "__main__":

    main()
from unittest.mock import patch

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


def build_incident():

    return IncidentInput(
        incident_id="RESILIENCE-001",
        source="resilience_test",
        timestamp="2026-08-31T20:40:00Z",
        latitude=47.490,
        longitude=19.080,
        disaster_type="explosion",
        severity="critical",
        affected_radius_km=0.5,
        population_density_per_km2=2800,
        description=(
            "ARES degraded-mode resilience test."
        ),
    )


def test_full_reachability_failure():

    orchestrator = ARESOrchestrator()

    incident = build_incident()

    with patch(
        "app.agents.network_agent.get_reachability_status"
    ) as mocked_reachability:

        mocked_reachability.side_effect = RuntimeError(
            "Simulated total CAMARA outage"
        )

        result = orchestrator.run_incident(
            incident=incident,
            responders=responder_teams,
            hospitals=hospitals,
            relief_centers=relief_centers,
        )

    assert (
        result["orchestration"]["status"]
        == "completed"
    )

    assert (
        result[
            "agentic_orchestration"
        ]["failed_calls"]
        == len(responder_teams)
    )

    for responder in result["responders"]:

        assert (
            responder[
                "reachable"
            ]
            is False
        )

        assert (
            responder[
                "eligible_for_deployment"
            ]
            is False
        )

    assert (
        result[
            "response_plan"
        ]["responder_assignments"]
        == []
    )

    print()
    print(
        "FULL REACHABILITY FAILURE: PASS"
    )

    print(
        "Orchestration status:",
        result[
            "orchestration"
        ]["status"],
    )

    print(
        "Failed CAMARA calls:",
        result[
            "agentic_orchestration"
        ]["failed_calls"],
    )

    print(
        "Responder assignments:",
        result[
            "response_plan"
        ]["responder_assignments"],
    )


def test_location_failure_fallback():

    orchestrator = ARESOrchestrator()

    incident = build_incident()

    def reachable_response(
        phone_number
    ):

        return {
            "reachable": True,
            "connectivity": [
                "SMS"
            ],
            "lastStatusTime":
                "2026-08-31T20:40:00Z",
        }

    with patch(
        "app.agents.network_agent.get_reachability_status",
        side_effect=reachable_response,
    ):

        with patch(
            "app.agents.network_agent.get_device_location"
        ) as mocked_location:

            mocked_location.side_effect = (
                RuntimeError(
                    "Simulated location outage"
                )
            )

            result = (
                orchestrator.run_incident(
                    incident=incident,
                    responders=responder_teams,
                    hospitals=hospitals,
                    relief_centers=(
                        relief_centers
                    ),
                )
            )

    assert (
        result["orchestration"]["status"]
        == "completed"
    )

    eligible_responders = [
        responder
        for responder
        in result["responders"]
        if responder[
            "eligible_for_deployment"
        ]
    ]

    assert len(
        eligible_responders
    ) > 0

    for responder in eligible_responders:

        assert (
            responder[
                "location_source"
            ]
            ==
            "registered_profile_fallback"
        )

        assert (
            responder[
                "network_degraded"
            ]
            is True
        )

    assert len(
        result[
            "response_plan"
        ]["responder_assignments"]
    ) > 0

    print()
    print(
        "LOCATION FAILURE FALLBACK: PASS"
    )

    print(
        "Eligible responders:",
        [
            responder["team_id"]
            for responder
            in eligible_responders
        ],
    )

    print(
        "Deployment assignments:",
        [
            assignment["team_id"]
            for assignment
            in result[
                "response_plan"
            ][
                "responder_assignments"
            ]
        ],
    )


if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "ARES FULL-PIPELINE RESILIENCE TESTS"
    )
    print("=" * 70)

    test_full_reachability_failure()

    test_location_failure_fallback()

    print()
    print("=" * 70)
    print(
        "ALL FULL-PIPELINE RESILIENCE TESTS PASSED"
    )
    print("=" * 70)

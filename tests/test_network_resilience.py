from unittest.mock import patch

from app.agents.network_agent import (
    NetworkIntelligenceAgent,
)


def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def test_reachability_failure():
    agent = NetworkIntelligenceAgent()

    with patch(
        "app.agents.network_agent.get_reachability_status"
    ) as mocked_call:

        mocked_call.side_effect = RuntimeError(
            "Simulated CAMARA timeout"
        )

        result = (
            agent.check_responder_reachability(
                "+99999991000"
            )
        )

    assert result["api_success"] is False
    assert result["reachable"] is False
    assert result["connectivity"] == []
    assert "Simulated CAMARA timeout" in result["error"]

    print("Reachability failure handling: PASS")
    print(result)


def test_location_failure():
    agent = NetworkIntelligenceAgent()

    with patch(
        "app.agents.network_agent.get_device_location"
    ) as mocked_call:

        mocked_call.side_effect = RuntimeError(
            "Simulated location timeout"
        )

        result = (
            agent.get_responder_location(
                "+99999991000"
            )
        )

    assert result["api_success"] is False
    assert result["latitude"] is None
    assert result["longitude"] is None
    assert "Simulated location timeout" in result["error"]

    print("Location failure handling: PASS")
    print(result)


def test_invalid_reachability_payload():
    agent = NetworkIntelligenceAgent()

    with patch(
        "app.agents.network_agent.get_reachability_status"
    ) as mocked_call:

        mocked_call.return_value = {
            "connectivity": ["SMS"]
        }

        result = (
            agent.check_responder_reachability(
                "+99999991000"
            )
        )

    assert result["api_success"] is False
    assert result["reachable"] is False
    assert "does not contain 'reachable'" in result["error"]

    print("Invalid reachability payload handling: PASS")
    print(result)


def test_invalid_location_payload():
    agent = NetworkIntelligenceAgent()

    with patch(
        "app.agents.network_agent.get_device_location"
    ) as mocked_call:

        mocked_call.return_value = {
            "area": {
                "center": {
                    "latitude": 500,
                    "longitude": 500,
                }
            }
        }

        result = (
            agent.get_responder_location(
                "+99999991000"
            )
        )

    assert result["api_success"] is False
    assert result["latitude"] is None
    assert result["longitude"] is None
    assert "outside valid ranges" in result["error"]

    print("Invalid location payload handling: PASS")
    print(result)


if __name__ == "__main__":

    print_section(
        "ARES NETWORK RESILIENCE TESTS"
    )

    test_reachability_failure()
    test_location_failure()
    test_invalid_reachability_payload()
    test_invalid_location_payload()

    print_section(
        "ALL NETWORK RESILIENCE TESTS PASSED"
    )
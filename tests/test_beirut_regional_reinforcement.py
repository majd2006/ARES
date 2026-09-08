from pprint import pprint

from app.agents.regional_reinforcement_agent import (
    RegionalReinforcementAgent,
)

from data.beirut_demo_scenario import (
    beirut_regional_hospitals,
    beirut_regional_relief_centers,
)


class DemoZone:
    latitude = 33.9014
    longitude = 35.5194


def main():

    agent = RegionalReinforcementAgent()

    forced_resource_escalation = {
        "status": "reinforcement_required",

        "reinforcement_requests": [

            {
                "resource_type": "hospital_capacity",
                "required_quantity": 150,
                "priority": "critical",
            },

            {
                "resource_type": "ambulances",
                "required_quantity": 10,
                "priority": "high",
            },

            {
                "resource_type": "medical_teams",
                "required_quantity": 5,
                "priority": "high",
            },

            {
                "resource_type": "volunteers",
                "required_quantity": 220,
                "priority": "medium",
            },
        ],
    }

    result = agent.generate_reinforcement_plan(
        disaster_zone=DemoZone(),
        resource_escalation=forced_resource_escalation,
        hospitals=beirut_regional_hospitals,
        relief_centers=beirut_regional_relief_centers,
    )

    print()
    print("=" * 72)
    print("BEIRUT REGIONAL REINFORCEMENT TEST")
    print("=" * 72)

    pprint(result)

    print()
    print("=" * 72)
    print("TEST COMPLETED")
    print("=" * 72)


if __name__ == "__main__":
    main()
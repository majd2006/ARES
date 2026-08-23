from app.agents.regional_reinforcement_agent import (
    RegionalReinforcementAgent,
)

from data.demo_scenario import (
    regional_hospitals,
    regional_relief_centers,
    disaster_zones,
)


agent = RegionalReinforcementAgent()

zone = disaster_zones[0]


resource_escalation = {

    "status":
        "critical",

    "reinforcement_requests": [

        {
            "resource_type":
                "hospital_capacity",

            "required_quantity":
                50,

            "priority":
                "critical",
        },

        {
            "resource_type":
                "ambulances",

            "required_quantity":
                4,

            "priority":
                "high",
        },

        {
            "resource_type":
                "medical_teams",

            "required_quantity":
                2,

            "priority":
                "high",
        },

        {
            "resource_type":
                "volunteers",

            "required_quantity":
                60,

            "priority":
                "medium",
        },
    ],
}


result = agent.generate_reinforcement_plan(
    disaster_zone=zone,
    resource_escalation=resource_escalation,
    hospitals=regional_hospitals,
    relief_centers=regional_relief_centers,
)


print(
    "ARES REGIONAL REINFORCEMENT"
)

print(
    "==========================="
)

print()

print(
    "Status:",
    result["status"].upper(),
)


print()
print(
    "Hospital Reinforcement"
)

print(
    "----------------------"
)

for allocation in result[
    "hospital_allocations"
]:

    print()

    print(
        allocation[
            "hospital_name"
        ]
    )

    print(
        "Distance:",
        allocation[
            "distance_km"
        ],
        "km",
    )

    print(
        "Additional capacity:",
        allocation[
            "allocated_capacity"
        ],
    )


print()
print(
    "Relief Reinforcement"
)

print(
    "--------------------"
)

for allocation in result[
    "relief_allocations"
]:

    print()

    print(
        allocation[
            "center_name"
        ]
    )

    print(
        allocation[
            "resource_type"
        ],
        ":",
        allocation[
            "quantity"
        ],
    )

    print(
        "Distance:",
        allocation[
            "distance_km"
        ],
        "km",
    )


print()
print(
    "Remaining Shortages"
)

print(
    "-------------------"
)

if result[
    "unmet_requirements"
]:

    for shortage in result[
        "unmet_requirements"
    ]:

        print(
            shortage
        )

else:

    print(
        "None"
    )


print()
print(
    "Summary"
)

print(
    "-------"
)

for key, value in (
    result[
        "summary"
    ].items()
):

    print(
        f"{key}: {value}"
    )
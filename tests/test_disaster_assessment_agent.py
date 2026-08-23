from app.agents.disaster_assessment_agent import (
    DisasterAssessmentAgent,
)


agent = DisasterAssessmentAgent()


assessment = agent.assess_disaster(
    disaster_type="explosion",
    severity="critical",
    affected_radius_km=0.5,
    population_density_per_km2=2800,
)


print("ARES DISASTER ASSESSMENT")
print("========================")

print()

print(
    "Disaster type:",
    assessment.disaster_type.upper(),
)

print(
    "Severity:",
    assessment.severity,
)

print()

print(
    "Affected radius:",
    assessment.affected_radius_km,
    "km",
)

print(
    "Affected area:",
    assessment.affected_area_km2,
    "km²",
)

print()

print(
    "Estimated population exposed:",
    assessment.estimated_population_exposed,
)

print(
    "Estimated casualties:",
    assessment.estimated_casualties,
)

print(
    "Estimated critical casualties:",
    assessment.estimated_critical,
)


print()
print("IMPACT ZONES")
print("------------")


for zone in assessment.impact_zones:

    print()

    print(zone.zone_name)

    print(
        f"Radius: "
        f"{zone.inner_radius_km} - "
        f"{zone.outer_radius_km} km"
    )

    print(
        f"Area: "
        f"{zone.area_km2} km²"
    )

    print(
        f"Population: "
        f"{zone.estimated_population}"
    )

    print(
        f"Estimated casualties: "
        f"{zone.estimated_casualties}"
    )

    print(
        f"Estimated critical: "
        f"{zone.estimated_critical}"
    )

    print(
        f"Casualty rate assumption: "
        f"{zone.casualty_rate * 100:.0f}%"
    )

    print(
        f"Critical rate assumption: "
        f"{zone.critical_rate * 100:.0f}%"
    )
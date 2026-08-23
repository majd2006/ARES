from app.agents.incident_ingestion_agent import (
    IncidentIngestionAgent,
    IncidentInput,
)


agent = IncidentIngestionAgent()


incoming_incident = IncidentInput(
    incident_id="INC-001",

    source="simulated_satellite_alert",

    timestamp="2026-08-20T18:00:00Z",

    latitude=47.490,
    longitude=19.080,

    disaster_type="blast",

    severity="extreme",

    affected_radius_km=0.5,

    population_density_per_km2=2800,

    description=(
        "Large explosion detected in a dense urban area."
    ),
)


incident = agent.ingest(
    incoming_incident
)


print("ARES INCIDENT INGESTION")
print("=======================")

print()

print(
    "Incident ID:",
    incident.incident_id,
)

print(
    "Source:",
    incident.source,
)

print(
    "Timestamp:",
    incident.timestamp,
)

print()

print(
    "Type:",
    incident.disaster_type.upper(),
)

print(
    "Severity:",
    incident.severity.upper(),
)

print()

print(
    "Location:",
    incident.latitude,
    incident.longitude,
)

print(
    "Affected radius:",
    incident.affected_radius_km,
    "km",
)

print(
    "Population density:",
    incident.population_density_per_km2,
    "people/km²",
)

print()

print(
    "Status:",
    incident.ingestion_status.upper(),
)
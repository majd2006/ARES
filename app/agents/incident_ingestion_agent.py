from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class IncidentInput:
    incident_id: str

    source: str
    timestamp: str

    latitude: float
    longitude: float

    disaster_type: str
    severity: str

    affected_radius_km: float
    population_density_per_km2: float

    description: Optional[str] = None


@dataclass
class NormalizedIncident:
    incident_id: str

    source: str
    timestamp: str

    latitude: float
    longitude: float

    disaster_type: str
    severity: str

    affected_radius_km: float
    population_density_per_km2: float

    description: str

    ingestion_status: str


class IncidentIngestionAgent:

    SUPPORTED_DISASTER_TYPES = {
        "explosion",
        "earthquake",
        "flood",
        "wildfire",
        "building_collapse",
        "industrial_accident",
    }

    VALID_SEVERITIES = {
        "moderate",
        "severe",
        "critical",
    }

    def normalize_disaster_type(
        self,
        disaster_type: str,
    ) -> str:

        value = (
            disaster_type
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        aliases = {
            "blast": "explosion",
            "fire": "wildfire",
            "collapse": "building_collapse",
            "industrial": "industrial_accident",
        }

        value = aliases.get(
            value,
            value,
        )

        if value not in self.SUPPORTED_DISASTER_TYPES:
            return "generic"

        return value

    def normalize_severity(
        self,
        severity: str,
    ) -> str:

        value = severity.strip().lower()

        aliases = {
            "high": "severe",
            "extreme": "critical",
            "major": "severe",
        }

        value = aliases.get(
            value,
            value,
        )

        if value not in self.VALID_SEVERITIES:
            return "moderate"

        return value

    def validate_coordinates(
        self,
        latitude: float,
        longitude: float,
    ):

        if not -90 <= latitude <= 90:
            raise ValueError(
                "Invalid latitude."
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                "Invalid longitude."
            )

    def validate_radius(
        self,
        radius_km: float,
    ):

        if radius_km <= 0:
            raise ValueError(
                "Affected radius must be greater than zero."
            )

    def validate_population_density(
        self,
        density: float,
    ):

        if density < 0:
            raise ValueError(
                "Population density cannot be negative."
            )

    def ingest(
        self,
        incident: IncidentInput,
    ) -> NormalizedIncident:

        self.validate_coordinates(
            incident.latitude,
            incident.longitude,
        )

        self.validate_radius(
            incident.affected_radius_km
        )

        self.validate_population_density(
            incident.population_density_per_km2
        )

        normalized_type = (
            self.normalize_disaster_type(
                incident.disaster_type
            )
        )

        normalized_severity = (
            self.normalize_severity(
                incident.severity
            )
        )

        description = (
            incident.description
            or "No additional incident description supplied."
        )

        timestamp = (
            incident.timestamp
            or datetime.utcnow().isoformat()
        )

        return NormalizedIncident(
            incident_id=incident.incident_id,

            source=incident.source,

            timestamp=timestamp,

            latitude=incident.latitude,
            longitude=incident.longitude,

            disaster_type=normalized_type,
            severity=normalized_severity,

            affected_radius_km=incident.affected_radius_km,

            population_density_per_km2=(
                incident.population_density_per_km2
            ),

            description=description,

            ingestion_status="accepted",
        )
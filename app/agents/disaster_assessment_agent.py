from dataclasses import dataclass
from math import pi


@dataclass
class ImpactZoneAssessment:
    zone_name: str

    inner_radius_km: float
    outer_radius_km: float

    area_km2: float

    estimated_population: int
    estimated_casualties: int
    estimated_critical: int

    casualty_rate: float
    critical_rate: float


@dataclass
class DisasterAssessment:
    disaster_type: str
    severity: str

    affected_radius_km: float
    affected_area_km2: float

    estimated_population_exposed: int
    estimated_casualties: int
    estimated_critical: int

    impact_zones: list


class DisasterAssessmentAgent:

    # ------------------------------------------------------
    # PROTOTYPE ZONE PROFILES
    #
    # These are hackathon/demo coefficients only.
    # They must not be presented as validated medical or
    # emergency-response casualty models.
    # ------------------------------------------------------

    EXPLOSION_ZONE_PROFILE = [
        {
            "name": "Severe Impact Zone",
            "inner_ratio": 0.0,
            "outer_ratio": 0.25,
            "casualty_rate": 0.70,
            "critical_rate": 0.45,
        },
        {
            "name": "Major Impact Zone",
            "inner_ratio": 0.25,
            "outer_ratio": 0.60,
            "casualty_rate": 0.35,
            "critical_rate": 0.25,
        },
        {
            "name": "Peripheral Impact Zone",
            "inner_ratio": 0.60,
            "outer_ratio": 1.0,
            "casualty_rate": 0.12,
            "critical_rate": 0.12,
        },
    ]

    GENERIC_ZONE_PROFILE = [
        {
            "name": "High Impact Zone",
            "inner_ratio": 0.0,
            "outer_ratio": 0.30,
            "casualty_rate": 0.40,
            "critical_rate": 0.30,
        },
        {
            "name": "Medium Impact Zone",
            "inner_ratio": 0.30,
            "outer_ratio": 0.65,
            "casualty_rate": 0.20,
            "critical_rate": 0.20,
        },
        {
            "name": "Low Impact Zone",
            "inner_ratio": 0.65,
            "outer_ratio": 1.0,
            "casualty_rate": 0.08,
            "critical_rate": 0.10,
        },
    ]

    def get_zone_profile(self, disaster_type: str):

        disaster_type = disaster_type.lower()

        if disaster_type == "explosion":
            return self.EXPLOSION_ZONE_PROFILE

        return self.GENERIC_ZONE_PROFILE

    @staticmethod
    def circle_area(radius_km: float) -> float:

        return pi * (radius_km ** 2)

    def ring_area(
        self,
        inner_radius_km: float,
        outer_radius_km: float,
    ) -> float:

        outer_area = self.circle_area(
            outer_radius_km
        )

        inner_area = self.circle_area(
            inner_radius_km
        )

        return outer_area - inner_area

    def assess_disaster(
        self,
        disaster_type: str,
        severity: str,
        affected_radius_km: float,
        population_density_per_km2: float,
    ) -> DisasterAssessment:

        zone_profile = self.get_zone_profile(
            disaster_type
        )

        impact_zones = []

        total_population = 0
        total_casualties = 0
        total_critical = 0

        for profile in zone_profile:

            inner_radius = (
                affected_radius_km
                * profile["inner_ratio"]
            )

            outer_radius = (
                affected_radius_km
                * profile["outer_ratio"]
            )

            area = self.ring_area(
                inner_radius,
                outer_radius,
            )

            population = round(
                area
                * population_density_per_km2
            )

            casualties = round(
                population
                * profile["casualty_rate"]
            )

            critical = round(
                casualties
                * profile["critical_rate"]
            )

            total_population += population
            total_casualties += casualties
            total_critical += critical

            impact_zones.append(
                ImpactZoneAssessment(
                    zone_name=profile["name"],

                    inner_radius_km=round(
                        inner_radius,
                        3,
                    ),

                    outer_radius_km=round(
                        outer_radius,
                        3,
                    ),

                    area_km2=round(
                        area,
                        3,
                    ),

                    estimated_population=population,

                    estimated_casualties=casualties,

                    estimated_critical=critical,

                    casualty_rate=profile[
                        "casualty_rate"
                    ],

                    critical_rate=profile[
                        "critical_rate"
                    ],
                )
            )

        total_area = self.circle_area(
            affected_radius_km
        )

        return DisasterAssessment(
            disaster_type=disaster_type.lower(),
            severity=severity.upper(),

            affected_radius_km=affected_radius_km,

            affected_area_km2=round(
                total_area,
                3,
            ),

            estimated_population_exposed=(
                total_population
            ),

            estimated_casualties=(
                total_casualties
            ),

            estimated_critical=(
                total_critical
            ),

            impact_zones=impact_zones,
        )
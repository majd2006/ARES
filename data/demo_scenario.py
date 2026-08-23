from app.models.resources import (
    ResponderTeam,
    Hospital,
    ReliefCenter,
    DisasterZone,
)

from app.agents.disaster_assessment_agent import (
    DisasterAssessmentAgent,
)


# ==========================================================
# RESPONDER TEAMS
# ==========================================================

responder_teams = [
    ResponderTeam(
        team_id="R01",
        name="Medical Team Alpha",
        phone_number="+99999991000",
        team_type="medical",
        members=8,
        available=True,
        latitude=47.4924,
        longitude=19.0810,
    ),

    ResponderTeam(
        team_id="R02",
        name="Rescue Team Bravo",
        phone_number="+99999991001",
        team_type="rescue",
        members=10,
        available=True,
        latitude=47.5015,
        longitude=19.0860,
    ),

    ResponderTeam(
        team_id="R03",
        name="Medical Team Charlie",
        phone_number="+99999991002",
        team_type="medical",
        members=6,
        available=True,
        latitude=47.5140,
        longitude=19.0950,
    ),

    ResponderTeam(
        team_id="R04",
        name="Rescue Team Delta",
        phone_number="+99999991003",
        team_type="rescue",
        members=12,
        available=True,
        latitude=47.4906,
        longitude=19.0802,
    ),
]


# ==========================================================
# HOSPITALS
# ==========================================================

hospitals = [
    Hospital(
        hospital_id="H01",
        name="Hospital A",
        latitude=47.495,
        longitude=19.085,
        total_capacity=150,
        available_capacity=80,
    ),

    Hospital(
        hospital_id="H02",
        name="Hospital B",
        latitude=47.475,
        longitude=19.070,
        total_capacity=220,
        available_capacity=140,
    ),
    
]


# ==========================================================
# RELIEF CENTERS
# ==========================================================

relief_centers = [
    ReliefCenter(
        center_id="RC01",
        name="Relief Center Alpha",
        latitude=47.480,
        longitude=19.090,
        available_volunteers=300,
        available_medical_teams=6,
        available_ambulances=14,
    ),
   
]
regional_hospitals = [
    Hospital(
        hospital_id="H03",
        name="Hospital C",
        latitude=47.515,
        longitude=19.105,
        total_capacity=180,
        available_capacity=95,
    ),

    Hospital(
        hospital_id="H04",
        name="Regional Trauma Center",
        latitude=47.458,
        longitude=19.045,
        total_capacity=300,
        available_capacity=170,
    ),
]


regional_relief_centers = [
    ReliefCenter(
        center_id="RC02",
        name="Relief Center Beta",
        latitude=47.505,
        longitude=19.102,
        available_volunteers=180,
        available_medical_teams=4,
        available_ambulances=8,
    ),

    ReliefCenter(
        center_id="RC03",
        name="Relief Center Gamma",
        latitude=47.462,
        longitude=19.055,
        available_volunteers=240,
        available_medical_teams=3,
        available_ambulances=6,
    ),
]

# ==========================================================
# DISASTER SCENARIO INPUT
# ==========================================================

disaster_scenario = {
    "disaster_type": "explosion",
    "severity": "critical",
    "latitude": 47.490,
    "longitude": 19.080,
    "affected_radius_km": 0.5,
    "population_density_per_km2": 2800,
}


# ==========================================================
# DISASTER ASSESSMENT
# ==========================================================

assessment_agent = DisasterAssessmentAgent()

assessment = assessment_agent.assess_disaster(
    disaster_type=disaster_scenario["disaster_type"],
    severity=disaster_scenario["severity"],
    affected_radius_km=disaster_scenario[
        "affected_radius_km"
    ],
    population_density_per_km2=disaster_scenario[
        "population_density_per_km2"
    ],
)

impact_zones = assessment.impact_zones


# ==========================================================
# GENERATED DISASTER ZONE
# ==========================================================

disaster_zones = [
    DisasterZone(
        zone_id="Z01",
        name="Critical Zone A",
        latitude=disaster_scenario["latitude"],
        longitude=disaster_scenario["longitude"],
        severity=assessment.severity.lower(),
        estimated_population=(
            assessment.estimated_population_exposed
        ),
        estimated_casualties=(
            assessment.estimated_casualties
        ),
        estimated_critical=(
            assessment.estimated_critical
        ),
    ),
]
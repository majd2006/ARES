from app.models.resources import (
    ResponderTeam,
    Hospital,
    ReliefCenter,
)


# ==========================================================
# BEIRUT PORT HISTORICAL DEMO SCENARIO
# ==========================================================
#
# IMPORTANT:
# These responder teams, hospitals, and relief centers are
# fictional demonstration resources.
#
# Their geographic placement is designed only to demonstrate
# ARES operational decision-making around Beirut Port.
#
# They must not be presented as historical records of actual
# emergency deployments during the 2020 Beirut Port explosion.
# ==========================================================


# ==========================================================
# INCIDENT LOCATION
# ==========================================================

BEIRUT_PORT_LATITUDE = 33.9014
BEIRUT_PORT_LONGITUDE = 35.5194


# ==========================================================
# RESPONDER TEAMS
# ==========================================================

beirut_responder_teams = [

    ResponderTeam(
        team_id="B-R01",
        name="Beirut Medical Team Alpha",
        phone_number="+99999991000",
        team_type="medical",
        members=8,

        latitude=33.8958,
        longitude=35.5138,

        available=True,
    ),

    ResponderTeam(
        team_id="B-R02",
        name="Beirut Rescue Team Bravo",
        phone_number="+99999991001",
        team_type="rescue",
        members=10,

        latitude=33.8931,
        longitude=35.5270,

        available=True,
    ),

    ResponderTeam(
        team_id="B-R03",
        name="Beirut Medical Team Charlie",
        phone_number="+99999991002",
        team_type="medical",
        members=6,

        latitude=33.8878,
        longitude=35.5078,

        available=True,
    ),

    # ------------------------------------------------------
    # Closest registered responder.
    #
    # Nokia Device Reachability for simulator number
    # +99999991003 currently reports this device unreachable.
    #
    # This provides the strongest network-aware decision
    # example in the demo:
    #
    # physically attractive candidate
    # -> network unreachable
    # -> excluded by ARES
    # ------------------------------------------------------

    ResponderTeam(
        team_id="B-R04",
        name="Beirut Rescue Team Delta",
        phone_number="+99999991003",
        team_type="rescue",
        members=12,

        latitude=33.9020,
        longitude=35.5198,

        available=True,
    ),
]


# ==========================================================
# LOCAL HOSPITALS
# ==========================================================

beirut_hospitals = [

    Hospital(
        hospital_id="B-H01",
        name="Beirut Emergency Hospital Alpha",

        latitude=33.8895,
        longitude=35.5057,

        total_capacity=150,
        available_capacity=80,
    ),

    Hospital(
        hospital_id="B-H02",
        name="Beirut Emergency Hospital Bravo",

        latitude=33.8789,
        longitude=35.5276,

        total_capacity=220,
        available_capacity=140,
    ),
]


# ==========================================================
# LOCAL RELIEF CENTERS
# ==========================================================

beirut_relief_centers = [

    ReliefCenter(
        center_id="B-RC01",
        name="Beirut Relief Center Alpha",

        latitude=33.8914,
        longitude=35.5165,

        available_volunteers=300,
        available_medical_teams=6,
        available_ambulances=14,
    ),
]


# ==========================================================
# REGIONAL HOSPITALS
# Simulated ARES regional reinforcement resources.
# These are fictional scenario assets, not real facilities.
# ==========================================================

beirut_regional_hospitals = [

    Hospital(
        hospital_id="B-H03",
        name="Jounieh Regional Hospital Alpha",

        latitude=33.9808,
        longitude=35.6175,

        total_capacity=220,
        available_capacity=120,
    ),

    Hospital(
        hospital_id="B-H04",
        name="Byblos Regional Hospital Bravo",

        latitude=34.1236,
        longitude=35.6511,

        total_capacity=180,
        available_capacity=95,
    ),

    Hospital(
        hospital_id="B-H05",
        name="Tripoli Regional Hospital Charlie",

        latitude=34.4333,
        longitude=35.8333,

        total_capacity=300,
        available_capacity=170,
    ),
]


# ==========================================================
# REGIONAL RELIEF CENTERS
# Simulated ARES regional reinforcement resources.
# These are fictional scenario assets, not real facilities.
# ==========================================================

beirut_regional_relief_centers = [

    ReliefCenter(
        center_id="B-RC02",
        name="Jounieh Regional Response Unit",

        latitude=33.9808,
        longitude=35.6175,

        available_volunteers=180,
        available_medical_teams=4,
        available_ambulances=8,
    ),

    ReliefCenter(
        center_id="B-RC03",
        name="Byblos Regional Response Unit",

        latitude=34.1236,
        longitude=35.6511,

        available_volunteers=140,
        available_medical_teams=3,
        available_ambulances=6,
    ),

    ReliefCenter(
        center_id="B-RC04",
        name="Tripoli Regional Response Unit",

        latitude=34.4333,
        longitude=35.8333,

        available_volunteers=260,
        available_medical_teams=6,
        available_ambulances=12,
    ),
]
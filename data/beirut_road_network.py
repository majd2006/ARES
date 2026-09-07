from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RoadCorridor:
    corridor_id: str
    name: str
    status: str
    reason: str

    # Approximate operational map geometry for the
    # Beirut historical demo scenario.
    # These coordinates are scenario geometry used
    # for visualization and route reasoning.
    coordinates: List[tuple[float, float]]

    alternative_corridor_id: Optional[str] = None


beirut_road_corridors = [

    RoadCorridor(
        corridor_id="BR-01",
        name="Charles Helou Avenue",
        status="blocked",
        reason=(
            "Simulated debris and restricted access "
            "near the incident zone."
        ),
        coordinates=[
            (33.8948, 35.5070),
            (33.8960, 35.5140),
            (33.8973, 35.5200),
            (33.8990, 35.5280),
        ],
        alternative_corridor_id="BR-03",
    ),

    RoadCorridor(
        corridor_id="BR-02",
        name="Armenia Street",
        status="congested",
        reason=(
            "Simulated evacuation and emergency "
            "traffic congestion."
        ),
        coordinates=[
            (33.8941, 35.5140),
            (33.8949, 35.5200),
            (33.8957, 35.5270),
        ],
        alternative_corridor_id="BR-03",
    ),

    RoadCorridor(
        corridor_id="BR-03",
        name="Gouraud Street",
        status="open",
        reason=(
            "Scenario corridor remains operational "
            "for emergency movement."
        ),
        coordinates=[
            (33.8940, 35.5050),
            (33.8943, 35.5100),
            (33.8946, 35.5140),
        ],
    ),

    RoadCorridor(
        corridor_id="BR-04",
        name="Al-Khoder / Karantina Access",
        status="blocked",
        reason=(
            "Direct access toward the incident zone "
            "is restricted in the demo scenario."
        ),
        coordinates=[
            (33.9020, 35.5198),
            (33.9005, 35.5215),
            (33.8990, 35.5230),
        ],
        alternative_corridor_id="BR-06",
    ),

    RoadCorridor(
        corridor_id="BR-05",
        name="Pierre Gemayel / Corniche El Nahr",
        status="open",
        reason=(
            "Scenario eastern approach remains "
            "available for responder deployment."
        ),
        coordinates=[
            (33.8870, 35.5200),
            (33.8900, 35.5230),
            (33.8940, 35.5260),
        ],
    ),

    RoadCorridor(
        corridor_id="BR-06",
        name="Emile Lahoud Axis",
        status="open",
        reason=(
            "Alternative north-south emergency "
            "approach remains available."
        ),
        coordinates=[
            (33.8875, 35.5310),
            (33.8935, 35.5295),
            (33.9000, 35.5280),
        ],
    ),

    RoadCorridor(
        corridor_id="BR-07",
        name="Forum de Beyrouth Approach",
        status="congested",
        reason=(
            "Simulated heavy emergency movement "
            "near the eastern port approach."
        ),
        coordinates=[
            (33.9010, 35.5260),
            (33.8995, 35.5280),
            (33.8978, 35.5295),
        ],
        alternative_corridor_id="BR-06",
    ),
]


def get_beirut_road_corridor(
    corridor_id: str,
) -> Optional[RoadCorridor]:

    for corridor in beirut_road_corridors:

        if corridor.corridor_id == corridor_id:
            return corridor

    return None
BEIRUT_RESPONDER_CORRIDORS = {
    "B-R01": "BR-01",
    "B-R02": "BR-05",
    "B-R03": "BR-02",
    "B-R04": "BR-04",
}


def get_responder_corridor_id(
    team_id: str,
) -> Optional[str]:

    return BEIRUT_RESPONDER_CORRIDORS.get(
        team_id
    )
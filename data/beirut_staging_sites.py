from dataclasses import dataclass
from typing import List


@dataclass
class StagingSite:
    site_id: str
    name: str
    latitude: float
    longitude: float
    corridor_id: str
    site_type: str
    notes: str


beirut_staging_sites: List[StagingSite] = [

    StagingSite(
        site_id="BS-01",
        name="East Beirut Field Staging Area",
        latitude=33.8960,
        longitude=35.5320,
        corridor_id="BR-05",
        site_type="field_medical_candidate",
        notes=(
            "Simulated staging location east of the "
            "incident for ARES prototype evaluation."
        ),
    ),

    StagingSite(
        site_id="BS-02",
        name="Central Beirut Field Staging Area",
        latitude=33.8930,
        longitude=35.5100,
        corridor_id="BR-03",
        site_type="field_medical_candidate",
        notes=(
            "Simulated staging location southwest of "
            "the incident for ARES prototype evaluation."
        ),
    ),

    StagingSite(
        site_id="BS-03",
        name="Northern Emergency Staging Area",
        latitude=33.9070,
        longitude=35.5350,
        corridor_id="BR-07",
        site_type="field_medical_candidate",
        notes=(
            "Simulated staging location northeast of "
            "the incident for ARES prototype evaluation."
        ),
    ),
]
from dataclasses import dataclass
from typing import List


@dataclass
class ResponderTeam:
    team_id: str
    name: str
    phone_number: str
    team_type: str
    members: int
    latitude: float
    longitude: float
    available: bool = True


@dataclass
class Ambulance:
    ambulance_id: str
    base_name: str
    available: bool = True


@dataclass
class Hospital:
    hospital_id: str
    name: str
    latitude: float
    longitude: float
    total_capacity: int
    available_capacity: int


@dataclass
class ReliefCenter:
    center_id: str
    name: str
    latitude: float
    longitude: float
    available_volunteers: int
    available_medical_teams: int
    available_ambulances: int


@dataclass
class DisasterZone:
    zone_id: str
    name: str
    latitude: float
    longitude: float
    severity: str
    estimated_population: int
    estimated_casualties: int
    estimated_critical: int
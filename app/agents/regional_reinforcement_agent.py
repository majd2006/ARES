from math import (
    radians,
    sin,
    cos,
    sqrt,
    atan2,
)
from app.optimization.resource_optimizer import (
    ResourceOptimizer,
)

class RegionalReinforcementAgent:

    EARTH_RADIUS_KM = 6371.0

    # ======================================================
    # DISTANCE
    # ======================================================
    
    def __init__(self):

        self.optimizer = (
            ResourceOptimizer()
    )

    def calculate_distance_km(
        self,
        lat1,
        lon1,
        lat2,
        lon2,
    ):

        lat1 = radians(lat1)
        lon1 = radians(lon1)

        lat2 = radians(lat2)
        lon2 = radians(lon2)

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1

        a = (
            sin(d_lat / 2) ** 2
            +
            cos(lat1)
            * cos(lat2)
            * sin(d_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return round(
            self.EARTH_RADIUS_KM * c,
            2,
        )

    # ======================================================
    # MAIN
    # ======================================================

    def generate_reinforcement_plan(
        self,
        disaster_zone,
        resource_escalation,
        hospitals,
        relief_centers,
    ):

        reinforcement_requests = (
            resource_escalation.get(
                "reinforcement_requests",
                [],
            )
        )

        hospital_allocations = []

        relief_allocations = []

        unmet_requirements = []

        # ==================================================
        # PROCESS EACH SHORTAGE
        # ==================================================

        for request in reinforcement_requests:

            resource_type = request[
                "resource_type"
            ]

            required_quantity = request[
                "required_quantity"
            ]

            # ------------------------------------------------
            # HOSPITAL CAPACITY
            # ------------------------------------------------

            if resource_type == "hospital_capacity":

                remaining = required_quantity

                hospital_candidates = []

                for hospital in hospitals:

                    if hospital.available_capacity <= 0:
                        continue

                    distance = (
                        self.calculate_distance_km(
                            disaster_zone.latitude,
                            disaster_zone.longitude,
                            hospital.latitude,
                            hospital.longitude,
                        )
                    )

                    hospital_candidates.append(
                        {
                            "hospital":
                                hospital,

                            "distance_km":
                                distance,
                        }
                    )

                # Closest useful hospital first
                optimized_candidates = (
    self.optimizer.rank_candidates(
        candidates=[
            {
                "hospital":
                    candidate[
                        "hospital"
                    ],

                "distance_km":
                    candidate[
                        "distance_km"
                    ],

                "available":
                    candidate[
                        "hospital"
                    ].available_capacity,
            }

            for candidate
            in hospital_candidates
        ],

        required_quantity=
            remaining,
    )
)

                for candidate in optimized_candidates:

                    if remaining <= 0:
                        break

                    hospital = (
                        candidate["hospital"]
                    )

                    allocated = min(
                        remaining,
                        hospital.available_capacity,
                    )

                    if allocated <= 0:
                        continue

                    hospital_allocations.append(
                        {
                            "hospital_id":
                                hospital.hospital_id,

                            "hospital_name":
                                hospital.name,

                            "distance_km":
                                candidate[
                                    "distance_km"
                                ],

                            "allocated_capacity":
                                allocated,

                            "available_capacity":
                                hospital.available_capacity,

                            "optimization_score":
                                candidate[
                                    "optimization"
                                ][
                                    "total_score"
                                ],

                            "mission":
                                (
                                    "Receive overflow "
                                    "critical patients"
                                ),
                        }
                    )

                    remaining -= allocated

                if remaining > 0:

                    unmet_requirements.append(
                        {
                            "resource_type":
                                "hospital_capacity",

                            "remaining_quantity":
                                remaining,

                            "severity":
                                "critical",
                        }
                    )

            # ------------------------------------------------
            # RELIEF CENTER RESOURCES
            # ------------------------------------------------

            elif resource_type in {
                "ambulances",
                "medical_teams",
                "volunteers",
            }:

                remaining = required_quantity

                relief_candidates = []

                for center in relief_centers:

                    if resource_type == "ambulances":

                        available = (
                            center
                            .available_ambulances
                        )

                    elif resource_type == "medical_teams":

                        available = (
                            center
                            .available_medical_teams
                        )

                    else:

                        available = (
                            center
                            .available_volunteers
                        )

                    if available <= 0:
                        continue

                    distance = (
                        self.calculate_distance_km(
                            disaster_zone.latitude,
                            disaster_zone.longitude,
                            center.latitude,
                            center.longitude,
                        )
                    )

                    relief_candidates.append(
                        {
                            "center":
                                center,

                            "available":
                                available,

                            "distance_km":
                                distance,
                        }
                    )

                optimized_candidates = (
                    self.optimizer.rank_candidates(
                        candidates=
                            relief_candidates,

                        required_quantity=
                            remaining,
                    )
                )

                for candidate in optimized_candidates:

                    if remaining <= 0:
                        break

                    center = (
                        candidate["center"]
                    )

                    allocated = min(
                        remaining,
                        candidate["available"],
                    )

                    if allocated <= 0:
                        continue

                    relief_allocations.append(
                        {
                            "center_id":
                                center.center_id,

                            "center_name":
                                center.name,

                            "resource_type":
                                resource_type,

                            "quantity":
                                allocated,

                            "distance_km":
                                candidate[
                                    "distance_km"
                                ],

                            "mission":
                                self._mission_for(
                                    resource_type
                                ),
                            "optimization_score":
                                candidate[
                                    "optimization"
                                ][
                                    "total_score"
                                ],
                        }
                    )

                    remaining -= allocated

                if remaining > 0:

                    unmet_requirements.append(
                        {
                            "resource_type":
                                resource_type,

                            "remaining_quantity":
                                remaining,

                            "severity":
                                request[
                                    "priority"
                                ],
                        }
                    )

        # ==================================================
        # STATUS
        # ==================================================

        if not reinforcement_requests:

            status = "not_required"

        elif unmet_requirements:

            status = "partial"

        else:

            status = "fully_allocated"

        return {
            "status":
                status,

            "hospital_allocations":
                hospital_allocations,

            "relief_allocations":
                relief_allocations,

            "unmet_requirements":
                unmet_requirements,

            "summary":
                self._build_summary(
                    hospital_allocations,
                    relief_allocations,
                    unmet_requirements,
                ),
        }

    # ======================================================
    # RESOURCE MISSIONS
    # ======================================================

    def _mission_for(
        self,
        resource_type,
    ):

        missions = {
            "ambulances":
                (
                    "Reinforce casualty evacuation "
                    "and hospital transport"
                ),

            "medical_teams":
                (
                    "Reinforce field triage "
                    "and emergency treatment"
                ),

            "volunteers":
                (
                    "Reinforce logistics, casualty "
                    "movement and field support"
                ),
        }

        return missions.get(
            resource_type,
            "Regional reinforcement",
        )

    # ======================================================
    # SUMMARY
    # ======================================================

    def _build_summary(
        self,
        hospital_allocations,
        relief_allocations,
        unmet_requirements,
    ):

        total_beds = sum(
            allocation[
                "allocated_capacity"
            ]
            for allocation
            in hospital_allocations
        )

        total_ambulances = sum(
            allocation["quantity"]
            for allocation
            in relief_allocations
            if allocation[
                "resource_type"
            ] == "ambulances"
        )

        total_medical_teams = sum(
            allocation["quantity"]
            for allocation
            in relief_allocations
            if allocation[
                "resource_type"
            ] == "medical_teams"
        )

        total_volunteers = sum(
            allocation["quantity"]
            for allocation
            in relief_allocations
            if allocation[
                "resource_type"
            ] == "volunteers"
        )

        return {
            "additional_hospital_capacity":
                total_beds,

            "additional_ambulances":
                total_ambulances,

            "additional_medical_teams":
                total_medical_teams,

            "additional_volunteers":
                total_volunteers,

            "remaining_shortages":
                len(
                    unmet_requirements
                ),
        }
from math import ceil


class ResponsePlanningAgent:

    def generate_plan(
        self,
        disaster_zone,
        responders,
        hospitals,
        relief_centers,
    ):
        critical = disaster_zone.estimated_critical
        casualties = disaster_zone.estimated_casualties

        total_medical_teams = sum(
            center.available_medical_teams
            for center in relief_centers
        )

        total_ambulances = sum(
            center.available_ambulances
            for center in relief_centers
        )

        total_volunteers = sum(
            center.available_volunteers
            for center in relief_centers
        )

        reachable_responders = [
            responder
            for responder in responders
            if responder.get("eligible_for_deployment")
        ]

        # -------------------------
        # RESOURCE REQUIREMENTS
        # -------------------------

        recommended_medical_teams = min(
            total_medical_teams,
            max(1, ceil(critical / 40)),
        )

        recommended_ambulances = min(
            total_ambulances,
            max(1, ceil(critical / 12)),
        )

        recommended_volunteers = min(
            total_volunteers,
            max(20, ceil(casualties * 0.35)),
        )

        # -------------------------
        # HOSPITAL ALLOCATION
        # -------------------------

        remaining_critical = critical
        hospital_allocations = []

        sorted_hospitals = sorted(
            hospitals,
            key=lambda hospital: hospital.available_capacity,
            reverse=True,
        )

        for hospital in sorted_hospitals:
            if remaining_critical <= 0:
                break

            allocation = min(
                hospital.available_capacity,
                remaining_critical,
            )

            hospital_allocations.append(
                {
                    "hospital_id": hospital.hospital_id,
                    "hospital_name": hospital.name,
                    "allocated_critical_patients": allocation,
                    "available_capacity": hospital.available_capacity,
                }
            )

            remaining_critical -= allocation

        # -------------------------
        # RESPONDER ASSIGNMENTS
        # -------------------------

        responder_assignments = []

        for index, responder in enumerate(
            reachable_responders,
            start=1,
        ):
            if responder["team_type"] == "medical":
                mission = "Medical response and triage"

            elif responder["team_type"] == "rescue":
                mission = "Search and rescue"

            else:
                mission = "General emergency support"

            responder_assignments.append(
                {
                    "priority": index,
                    "team_id": responder["team_id"],
                    "name": responder["name"],
                    "team_type": responder["team_type"],
                    "mission": mission,
                    "distance_km": responder[
                        "distance_to_disaster_km"
                    ],
                    "network_status": (
                        "reachable"
                        if responder["reachable"]
                        else "unreachable"
                    ),
                }
            )

        # -------------------------
        # PLAN
        # -------------------------

        return {
            "zone_id": disaster_zone.zone_id,
            "zone_name": disaster_zone.name,
            "severity": disaster_zone.severity,
            "recommended_resources": {
                "medical_teams": recommended_medical_teams,
                "ambulances": recommended_ambulances,
                "volunteers": recommended_volunteers,
            },
            "responder_assignments": responder_assignments,
            "hospital_allocations": hospital_allocations,
            "unallocated_critical_patients": remaining_critical,
            "reserve_resources": {
                "medical_teams": (
                    total_medical_teams
                    - recommended_medical_teams
                ),
                "ambulances": (
                    total_ambulances
                    - recommended_ambulances
                ),
                "volunteers": (
                    total_volunteers
                    - recommended_volunteers
                ),
            },
        }
from math import ceil

class FieldMedicalPostAgent:

    def evaluate(
        self,
        disaster_zone,
        response_plan,
        hospitals,
        relief_centers,
    ):
        critical = (
            disaster_zone.estimated_critical
        )

        casualties = (
            disaster_zone.estimated_casualties
        )

        total_hospital_capacity = sum(
            hospital.available_capacity
            for hospital in hospitals
        )

        allocated_critical = sum(
            allocation[
                "allocated_critical_patients"
            ]
            for allocation
            in response_plan[
                "hospital_allocations"
            ]
        )

        unallocated_critical = (
            response_plan[
                "unallocated_critical_patients"
            ]
        )

        if total_hospital_capacity > 0:
            projected_hospital_pressure = (
                critical
                /
                total_hospital_capacity
            )
        else:
            projected_hospital_pressure = 1.0

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

        # --------------------------------------------------
        # ACTIVATION POLICY
        # --------------------------------------------------

        reasons = []

        if unallocated_critical > 0:
            reasons.append(
                (
                    f"{unallocated_critical} critical patients "
                    "exceed available local hospital capacity."
                )
            )

        if projected_hospital_pressure >= 0.50:
            reasons.append(
                (
                    "Projected critical-patient demand "
                    f"uses {round(projected_hospital_pressure * 100)}% "
                    "of currently available local hospital capacity."
                )
            )

        if casualties >= 300:
            reasons.append(
                (
                    "Estimated casualty volume exceeds the "
                    "mass-casualty field-support threshold."
                )
            )

        required = bool(reasons)

        # --------------------------------------------------
        # NO ACTIVATION
        # --------------------------------------------------

        if not required:
            return {
                "required": False,
                "status": "not_required",
                "reason": (
                    "Current casualty volume and hospital "
                    "pressure do not require a field medical post."
                ),
                "activation_reasons": [],
                "recommended_posts": 0,
                "medical_teams_required": 0,
                "ambulances_required": 0,
                "volunteers_required": 0,
                "capabilities": [],
                "projected_hospital_pressure": round(
                    projected_hospital_pressure,
                    3,
                ),
                "allocated_critical_patients":
                    allocated_critical,
                "unallocated_critical_patients":
                    unallocated_critical,
            }

        # --------------------------------------------------
        # FIELD POST REQUIREMENTS
        # --------------------------------------------------

        recommended_posts = max(
            1,
            ceil(casualties / 500),
        )

        # Allocate field-post staffing from the mobilized response plan.
        mobilized = response_plan["recommended_resources"]

        medical_teams_required = min(
            mobilized["medical_teams"],
            total_medical_teams,
            max(
                1,
                recommended_posts * 2,
            ),
        )

        ambulances_required = min(
            mobilized["ambulances"],
            total_ambulances,
            max(
                1,
                recommended_posts * 2,
            ),
        )

        volunteers_required = min(
            mobilized["volunteers"],
            total_volunteers,
            max(
                20,
                recommended_posts * 30,
            ),
        )

        return {
            "required": True,
            "status": "recommended",
            "reason": reasons[0],
            "activation_reasons": reasons,
            "recommended_posts":
                recommended_posts,
            "medical_teams_required":
                medical_teams_required,
            "ambulances_required":
                ambulances_required,
            "volunteers_required":
                volunteers_required,
            "capabilities": [
                "triage",
                "stabilization",
                "minor_and_moderate_care",
                "evacuation_staging",
            ],
            "projected_hospital_pressure": round(
                projected_hospital_pressure,
                3,
            ),
            "allocated_critical_patients":
                allocated_critical,
            "unallocated_critical_patients":
                unallocated_critical,
        }
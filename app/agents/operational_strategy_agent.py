class OperationalStrategyAgent:

    def generate_strategy(
        self,
        disaster_zone,
        response_plan,
        all_responders,
    ):
        actions = []

        # --------------------------------------------------
        # 1. INCIDENT PRIORITY
        # --------------------------------------------------

        actions.append(
            {
                "priority": 1,
                "category": "Incident Command",
                "title": "Activate critical response posture",
                "description": (
                    f"{disaster_zone.name} is classified as "
                    f"{disaster_zone.severity.upper()} with "
                    f"{disaster_zone.estimated_critical} estimated "
                    "critical casualties."
                ),
            }
        )

        # --------------------------------------------------
        # 2. RESPONDER DEPLOYMENT
        # --------------------------------------------------

        for assignment in response_plan["responder_assignments"]:
            actions.append(
                {
                    "priority": len(actions) + 1,
                    "category": "Responder Deployment",
                    "title": (
                        f"Deploy {assignment['name']}"
                    ),
                    "description": (
                        f"Assign {assignment['name']} to "
                        f"{assignment['mission']}. "
                        f"Current distance: "
                        f"{assignment['distance_km']} km. "
                        f"Network status: "
                        f"{assignment['network_status'].upper()}."
                    ),
                }
            )

        # --------------------------------------------------
        # 3. EXCLUDED / UNREACHABLE RESPONDERS
        # --------------------------------------------------

        unreachable = [
            responder
            for responder in all_responders
            if not responder.get("reachable", False)
        ]

        for responder in unreachable:
            actions.append(
                {
                    "priority": len(actions) + 1,
                    "category": "Network Constraint",
                    "title": (
                        f"Do not dispatch {responder['name']}"
                    ),
                    "description": (
                        f"{responder['name']} is currently "
                        f"{responder['distance_to_disaster_km']} km "
                        "from the incident but is excluded because "
                        "Nokia Network-as-Code reports the unit as "
                        "unreachable."
                    ),
                }
            )

        # --------------------------------------------------
        # 4. MEDICAL RESOURCE MOBILIZATION
        # --------------------------------------------------

        resources = response_plan["recommended_resources"]

        actions.append(
            {
                "priority": len(actions) + 1,
                "category": "Medical Response",
                "title": "Mobilize medical resources",
                "description": (
                    f"Deploy {resources['medical_teams']} medical "
                    f"teams and {resources['ambulances']} ambulances "
                    f"to support treatment and evacuation of "
                    f"{disaster_zone.estimated_casualties} estimated "
                    "casualties."
                ),
            }
        )

        # --------------------------------------------------
        # 5. VOLUNTEER MOBILIZATION
        # --------------------------------------------------

        actions.append(
            {
                "priority": len(actions) + 1,
                "category": "Field Support",
                "title": "Mobilize volunteer support",
                "description": (
                    f"Deploy {resources['volunteers']} volunteers "
                    "for logistics, casualty movement, field support, "
                    "and coordination tasks."
                ),
            }
        )

        # --------------------------------------------------
        # 6. HOSPITAL ALLOCATION
        # --------------------------------------------------

        for allocation in response_plan["hospital_allocations"]:
            actions.append(
                {
                    "priority": len(actions) + 1,
                    "category": "Medical Evacuation",
                    "title": (
                        f"Route critical patients to "
                        f"{allocation['hospital_name']}"
                    ),
                    "description": (
                        f"Allocate up to "
                        f"{allocation['allocated_critical_patients']} "
                        "critical patients to "
                        f"{allocation['hospital_name']} based on "
                        "currently available capacity."
                    ),
                }
            )

        # --------------------------------------------------
        # 7. RESERVE
        # --------------------------------------------------

        reserve = response_plan["reserve_resources"]

        actions.append(
            {
                "priority": len(actions) + 1,
                "category": "Operational Reserve",
                "title": "Maintain emergency reserve",
                "description": (
                    f"Keep {reserve['medical_teams']} medical teams, "
                    f"{reserve['ambulances']} ambulances, and "
                    f"{reserve['volunteers']} volunteers in reserve "
                    "for escalation or secondary incidents."
                ),
            }
        )

        # --------------------------------------------------
        # 8. CAPACITY WARNING
        # --------------------------------------------------

        if response_plan["unallocated_critical_patients"] > 0:
            actions.append(
                {
                    "priority": len(actions) + 1,
                    "category": "Capacity Warning",
                    "title": "Hospital capacity shortfall detected",
                    "description": (
                        f"{response_plan['unallocated_critical_patients']} "
                        "critical patients remain without assigned "
                        "hospital capacity. Escalate to additional "
                        "medical facilities or temporary field care."
                    ),
                }
            )

        return {
            "headline": (
                "ARES Operational Strategy"
            ),
            "incident": disaster_zone.name,
            "severity": disaster_zone.severity,
            "actions": actions,
        }
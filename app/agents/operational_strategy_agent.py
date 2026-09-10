class OperationalStrategyAgent:

    def generate_strategy(
        self,
        disaster_zone,
        response_plan,
        all_responders,
        field_medical_post=None,
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
                        + (
                            "a simulated runtime network override marks the unit "
                            "unreachable; this is not a Nokia-delivered outage."
                            if responder.get("runtime_network_override", False)
                            else "Nokia Network-as-Code reports the unit as unreachable."
                        )
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
        # 6. FIELD MEDICAL POST
        # --------------------------------------------------

        if (
            field_medical_post
            and field_medical_post.get(
                "required",
                False,
            )
        ):

            actions.append(
                {
                    "priority":
                        len(actions) + 1,

                    "category":
                        "Field Medical Support",

                    "title":
                        (
                            "Establish field medical "
                            "and triage post"
                        ),

                    "description":
                        (
                            f"Establish "
                            f"{field_medical_post['recommended_posts']} "
                            "field medical post to provide triage, "
                            "stabilization, minor and moderate care, "
                            "and evacuation staging."
                        ),
                }
            )

            actions.append(
                {
                    "priority":
                        len(actions) + 1,

                    "category":
                        "Field Resource Allocation",

                    "title":
                        "Allocate field medical resources",

                    "description":
                        (
                            f"Assign "
                            f"{field_medical_post['medical_teams_required']} "
                            "medical teams, "
                            f"{field_medical_post['ambulances_required']} "
                            "ambulances, and "
                            f"{field_medical_post['volunteers_required']} "
                            "volunteers from the mobilized response resources "
                            "to field medical operations."
                        ),
                }
            )

            actions.append(
                {
                    "priority":
                        len(actions) + 1,

                    "category":
                        "Medical Flow",

                    "title":
                        "Separate field treatment from hospital evacuation",

                    "description":
                        (
                            "Use the field medical post for triage, "
                            "stabilization, minor and moderate care, "
                            "and evacuation staging while reserving "
                            "hospital transport for patients requiring "
                            "hospital-level treatment."
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

        reserve_title = "Maintain emergency reserve"
        reserve_description = (
            f"Keep {reserve['medical_teams']} medical teams, "
            f"{reserve['ambulances']} ambulances, and "
            f"{reserve['volunteers']} volunteers in reserve "
            "for escalation or secondary incidents."
        )

        exhausted = [
            label for key, label in (
                ("medical_teams", "medical-team"),
                ("ambulances", "ambulance"),
            ) if reserve[key] == 0
        ]
        if exhausted:
            reserve_title = "Address local reserve exhaustion"
            available = [
                f"{reserve[key]} {label}" for key, label in (
                    ("medical_teams", "medical teams"),
                    ("ambulances", "ambulances"),
                    ("volunteers", "volunteers"),
                ) if reserve[key] > 0
            ]
            reserve_description = (
                f"Local {' and '.join(exhausted)} reserves are exhausted. "
            )
            if available:
                reserve_description += (
                    f"Maintain {' and '.join(available)} in reserve and "
                    "activate resource escalation for additional medical "
                    "and transport capacity."
                )
            else:
                reserve_description += (
                    "No local operational reserves remain. Activate resource "
                    "escalation for additional medical and transport capacity."
                )

        actions.append(
            {
                "priority": len(actions) + 1,
                "category": "Operational Reserve",
                "title": reserve_title,
                "description": reserve_description,
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
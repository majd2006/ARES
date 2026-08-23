class ResourceEscalationAgent:

    def evaluate(
        self,
        response_plan,
        hospitals,
        relief_centers,
    ):
        alerts = []
        requests = []

        reserve = response_plan["reserve_resources"]

        unallocated_critical = (
            response_plan[
                "unallocated_critical_patients"
            ]
        )

        # --------------------------------------------------
        # HOSPITAL CAPACITY
        # --------------------------------------------------

        if unallocated_critical > 0:
            alerts.append(
                {
                    "type": "hospital_capacity",
                    "severity": "critical",
                    "message": (
                        f"{unallocated_critical} critical patients "
                        "remain without assigned hospital capacity."
                    ),
                }
            )

            requests.append(
                {
                    "resource_type":
                        "hospital_capacity",

                    "required_quantity":
                        unallocated_critical,

                    "priority":
                        "critical",

                    "action":
                        (
                            "Request additional regional hospital "
                            "capacity or activate temporary field "
                            "medical capability."
                        ),
                }
            )

        # --------------------------------------------------
        # AMBULANCE RESERVE
        # --------------------------------------------------

        if reserve["ambulances"] <= 0:
            alerts.append(
                {
                    "type": "ambulance_exhaustion",
                    "severity": "high",
                    "message": (
                        "Local ambulance reserve is exhausted."
                    ),
                }
            )

            requests.append(
                {
                    "resource_type":
                        "ambulances",

                    "required_quantity":
                        max(
                            2,
                            round(
                                response_plan[
                                    "recommended_resources"
                                ]["ambulances"]
                                * 0.25
                            ),
                        ),

                    "priority":
                        "high",

                    "action":
                        (
                            "Request ambulance reinforcement "
                            "from neighboring relief centers."
                        ),
                }
            )

        # --------------------------------------------------
        # MEDICAL TEAM RESERVE
        # --------------------------------------------------

        if reserve["medical_teams"] <= 0:
            alerts.append(
                {
                    "type": "medical_team_exhaustion",
                    "severity": "high",
                    "message": (
                        "No medical teams remain in operational reserve."
                    ),
                }
            )

            requests.append(
                {
                    "resource_type":
                        "medical_teams",

                    "required_quantity":
                        max(
                            1,
                            round(
                                response_plan[
                                    "recommended_resources"
                                ]["medical_teams"]
                                * 0.25
                            ),
                        ),

                    "priority":
                        "high",

                    "action":
                        (
                            "Request additional medical teams "
                            "from regional response partners."
                        ),
                }
            )

        # --------------------------------------------------
        # VOLUNTEER RESERVE
        # --------------------------------------------------

        if reserve["volunteers"] <= 0:
            alerts.append(
                {
                    "type": "volunteer_exhaustion",
                    "severity": "medium",
                    "message": (
                        "Local volunteer reserve is exhausted."
                    ),
                }
            )

            requests.append(
                {
                    "resource_type":
                        "volunteers",

                    "required_quantity":
                        max(
                            25,
                            round(
                                response_plan[
                                    "recommended_resources"
                                ]["volunteers"]
                                * 0.20
                            ),
                        ),

                    "priority":
                        "medium",

                    "action":
                        (
                            "Mobilize additional volunteers "
                            "from neighboring relief centers."
                        ),
                }
            )

        # --------------------------------------------------
        # OVERALL STATUS
        # --------------------------------------------------

        if not alerts:
            status = "stable"
        elif any(
            alert["severity"] == "critical"
            for alert in alerts
        ):
            status = "critical"
        else:
            status = "reinforcement_required"

        return {
            "status": status,
            "alerts": alerts,
            "reinforcement_requests": requests,
        }
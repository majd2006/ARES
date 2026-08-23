class IncidentReassessmentAgent:

    def compare(
        self,
        previous_incident: dict,
        current_incident: dict,
    ):

        changes = []
        requires_replanning = False

        # --------------------------------------------------
        # RADIUS CHANGE
        # --------------------------------------------------

        previous_radius = previous_incident.get(
            "affected_radius_km"
        )

        current_radius = current_incident.get(
            "affected_radius_km"
        )

        if (
            previous_radius is not None
            and current_radius is not None
            and previous_radius != current_radius
        ):

            direction = (
                "increased"
                if current_radius > previous_radius
                else "decreased"
            )

            changes.append(
                {
                    "type": "affected_radius",
                    "severity": "high",
                    "message": (
                        f"Affected radius {direction} "
                        f"from {previous_radius} km "
                        f"to {current_radius} km."
                    ),
                }
            )

            requires_replanning = True

        # --------------------------------------------------
        # EXPOSED POPULATION CHANGE
        # --------------------------------------------------

        previous_population = previous_incident.get(
            "estimated_population"
        )

        current_population = current_incident.get(
            "estimated_population"
        )

        if (
            previous_population is not None
            and current_population is not None
            and previous_population != current_population
        ):

            difference = (
                current_population
                - previous_population
            )

            changes.append(
                {
                    "type": "population_exposure",
                    "severity": "high",
                    "message": (
                        "Estimated exposed population "
                        f"changed by {difference:+d} people "
                        f"({previous_population} → "
                        f"{current_population})."
                    ),
                }
            )

            requires_replanning = True

        # --------------------------------------------------
        # CASUALTY CHANGE
        # --------------------------------------------------

        previous_casualties = previous_incident.get(
            "estimated_casualties"
        )

        current_casualties = current_incident.get(
            "estimated_casualties"
        )

        if (
            previous_casualties is not None
            and current_casualties is not None
            and previous_casualties != current_casualties
        ):

            difference = (
                current_casualties
                - previous_casualties
            )

            changes.append(
                {
                    "type": "casualty_estimate",
                    "severity": "critical"
                    if difference > 0
                    else "medium",

                    "message": (
                        "Estimated casualties changed "
                        f"by {difference:+d} "
                        f"({previous_casualties} → "
                        f"{current_casualties})."
                    ),
                }
            )

            requires_replanning = True

        # --------------------------------------------------
        # CRITICAL CASUALTY CHANGE
        # --------------------------------------------------

        previous_critical = previous_incident.get(
            "estimated_critical"
        )

        current_critical = current_incident.get(
            "estimated_critical"
        )

        if (
            previous_critical is not None
            and current_critical is not None
            and previous_critical != current_critical
        ):

            difference = (
                current_critical
                - previous_critical
            )

            changes.append(
                {
                    "type": "critical_casualties",
                    "severity": "critical"
                    if difference > 0
                    else "medium",

                    "message": (
                        "Estimated critical casualties "
                        f"changed by {difference:+d} "
                        f"({previous_critical} → "
                        f"{current_critical})."
                    ),
                }
            )

            requires_replanning = True

        # --------------------------------------------------
        # SEVERITY CHANGE
        # --------------------------------------------------

        previous_severity = previous_incident.get(
            "severity"
        )

        current_severity = current_incident.get(
            "severity"
        )

        if (
            previous_severity
            and current_severity
            and previous_severity != current_severity
        ):

            changes.append(
                {
                    "type": "severity",
                    "severity": "critical",
                    "message": (
                        "Incident severity changed "
                        f"from {previous_severity.upper()} "
                        f"to {current_severity.upper()}."
                    ),
                }
            )

            requires_replanning = True

        # --------------------------------------------------
        # OVERALL STATUS
        # --------------------------------------------------

        if not changes:
            status = "stable"

        elif requires_replanning:
            status = "replanning_required"

        else:
            status = "updated"

        return {
            "status": status,
            "requires_replanning":
                requires_replanning,
            "change_count":
                len(changes),
            "changes":
                changes,
        }
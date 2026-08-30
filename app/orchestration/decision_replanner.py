class DecisionReplanner:
    """
    Compare two complete ARES decisions and explain
    what changed operationally.

    This agent does not generate the new response plan.
    ARESOrchestrator generates the new decision.

    DecisionReplanner compares:
        Decision N
            vs
        Decision N+1

    and produces an explainable operational delta.
    """

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _responders_by_id(decision):

        return {
            responder["team_id"]: responder
            for responder in decision.get(
                "responders",
                [],
            )
        }

    @staticmethod
    def _assignments_by_id(decision):

        plan = decision.get(
            "response_plan",
            {},
        )

        return {
            assignment["team_id"]: assignment
            for assignment in plan.get(
                "responder_assignments",
                [],
            )
        }

    # ======================================================
    # RESPONDER STATE CHANGES
    # ======================================================

    def _compare_responder_states(
        self,
        previous_decision,
        current_decision,
    ):

        changes = []

        previous_responders = (
            self._responders_by_id(
                previous_decision
            )
        )

        current_responders = (
            self._responders_by_id(
                current_decision
            )
        )

        team_ids = set(
            previous_responders
        ) | set(
            current_responders
        )

        for team_id in sorted(
            team_ids
        ):

            previous = (
                previous_responders.get(
                    team_id
                )
            )

            current = (
                current_responders.get(
                    team_id
                )
            )

            if not previous or not current:
                continue

            # ------------------------------------------
            # REACHABILITY CHANGE
            # ------------------------------------------

            if (
                previous.get(
                    "reachable"
                )
                != current.get(
                    "reachable"
                )
            ):

                changes.append(
                    {
                        "type":
                            "network_reachability",

                        "team_id":
                            team_id,

                        "team_name":
                            current.get(
                                "name"
                            ),

                        "previous":
                            previous.get(
                                "reachable"
                            ),

                        "current":
                            current.get(
                                "reachable"
                            ),

                        "severity":
                            (
                                "critical"
                                if not current.get(
                                    "reachable"
                                )
                                else "medium"
                            ),

                        "message":
                            (
                                f"{current.get('name')} "
                                "changed network state "
                                f"from "
                                f"{'reachable' if previous.get('reachable') else 'unreachable'} "
                                "to "
                                f"{'reachable' if current.get('reachable') else 'unreachable'}."
                            ),
                    }
                )

            # ------------------------------------------
            # ELIGIBILITY CHANGE
            # ------------------------------------------

            if (
                previous.get(
                    "eligible_for_deployment"
                )
                != current.get(
                    "eligible_for_deployment"
                )
            ):

                changes.append(
                    {
                        "type":
                            "deployment_eligibility",

                        "team_id":
                            team_id,

                        "team_name":
                            current.get(
                                "name"
                            ),

                        "previous":
                            previous.get(
                                "eligible_for_deployment"
                            ),

                        "current":
                            current.get(
                                "eligible_for_deployment"
                            ),

                        "severity":
                            (
                                "critical"
                                if not current.get(
                                    "eligible_for_deployment"
                                )
                                else "medium"
                            ),

                        "message":
                            (
                                f"{current.get('name')} "
                                "deployment eligibility "
                                "changed."
                            ),
                    }
                )

        return changes

    # ======================================================
    # ASSIGNMENT CHANGES
    # ======================================================

    def _compare_assignments(
        self,
        previous_decision,
        current_decision,
    ):

        changes = []

        previous_assignments = (
            self._assignments_by_id(
                previous_decision
            )
        )

        current_assignments = (
            self._assignments_by_id(
                current_decision
            )
        )

        # ----------------------------------------------
        # REMOVED TEAMS
        # ----------------------------------------------

        removed = (
            set(previous_assignments)
            - set(current_assignments)
        )

        for team_id in sorted(
            removed
        ):

            assignment = (
                previous_assignments[
                    team_id
                ]
            )

            changes.append(
                {
                    "type":
                        "deployment_removed",

                    "team_id":
                        team_id,

                    "team_name":
                        assignment.get(
                            "name"
                        ),

                    "severity":
                        "critical",

                    "message":
                        (
                            f"{assignment.get('name')} "
                            "was removed from the "
                            "active deployment plan."
                        ),
                }
            )

        # ----------------------------------------------
        # ADDED TEAMS
        # ----------------------------------------------

        added = (
            set(current_assignments)
            - set(previous_assignments)
        )

        for team_id in sorted(
            added
        ):

            assignment = (
                current_assignments[
                    team_id
                ]
            )

            changes.append(
                {
                    "type":
                        "deployment_added",

                    "team_id":
                        team_id,

                    "team_name":
                        assignment.get(
                            "name"
                        ),

                    "severity":
                        "high",

                    "message":
                        (
                            f"{assignment.get('name')} "
                            "was added to the active "
                            "deployment plan."
                        ),
                }
            )

        # ----------------------------------------------
        # PRIORITY CHANGES
        # ----------------------------------------------

        common = (
            set(previous_assignments)
            & set(current_assignments)
        )

        for team_id in sorted(
            common
        ):

            previous = (
                previous_assignments[
                    team_id
                ]
            )

            current = (
                current_assignments[
                    team_id
                ]
            )

            if (
                previous.get(
                    "priority"
                )
                != current.get(
                    "priority"
                )
            ):

                changes.append(
                    {
                        "type":
                            "deployment_priority",

                        "team_id":
                            team_id,

                        "team_name":
                            current.get(
                                "name"
                            ),

                        "previous":
                            previous.get(
                                "priority"
                            ),

                        "current":
                            current.get(
                                "priority"
                            ),

                        "severity":
                            "medium",

                        "message":
                            (
                                f"{current.get('name')} "
                                "deployment priority "
                                f"changed from "
                                f"{previous.get('priority')} "
                                f"to "
                                f"{current.get('priority')}."
                            ),
                    }
                )

        return changes

    # ======================================================
    # RESOURCE CHANGES
    # ======================================================

    @staticmethod
    def _compare_resources(
        previous_decision,
        current_decision,
    ):

        changes = []

        previous_resources = (
            previous_decision.get(
                "response_plan",
                {},
            ).get(
                "recommended_resources",
                {},
            )
        )

        current_resources = (
            current_decision.get(
                "response_plan",
                {},
            ).get(
                "recommended_resources",
                {},
            )
        )

        resource_names = {
            "medical_teams":
                "medical teams",

            "ambulances":
                "ambulances",

            "volunteers":
                "volunteers",
        }

        for (
            resource_key,
            display_name,
        ) in resource_names.items():

            previous_value = (
                previous_resources.get(
                    resource_key
                )
            )

            current_value = (
                current_resources.get(
                    resource_key
                )
            )

            if (
                previous_value is not None
                and current_value is not None
                and previous_value
                != current_value
            ):

                changes.append(
                    {
                        "type":
                            "resource_requirement",

                        "resource":
                            resource_key,

                        "previous":
                            previous_value,

                        "current":
                            current_value,

                        "severity":
                            (
                                "high"
                                if current_value
                                > previous_value
                                else "medium"
                            ),

                        "message":
                            (
                                f"Required {display_name} "
                                f"changed from "
                                f"{previous_value} "
                                f"to {current_value}."
                            ),
                    }
                )

        return changes

    # ======================================================
    # INCIDENT CHANGES
    # ======================================================

    @staticmethod
    def _compare_incident(
        previous_decision,
        current_decision,
    ):

        changes = []

        previous_assessment = (
            previous_decision.get(
                "assessment",
                {},
            )
        )

        current_assessment = (
            current_decision.get(
                "assessment",
                {},
            )
        )

        fields = {
            "affected_radius_km":
                "Affected radius",

            "estimated_population_exposed":
                "Estimated exposed population",

            "estimated_casualties":
                "Estimated casualties",

            "estimated_critical":
                "Estimated critical casualties",

            "severity":
                "Incident severity",
        }

        for (
            field,
            display_name,
        ) in fields.items():

            previous_value = (
                previous_assessment.get(
                    field
                )
            )

            current_value = (
                current_assessment.get(
                    field
                )
            )

            if (
                previous_value
                != current_value
            ):

                changes.append(
                    {
                        "type":
                            "incident_state",

                        "field":
                            field,

                        "previous":
                            previous_value,

                        "current":
                            current_value,

                        "severity":
                            "high",

                        "message":
                            (
                                f"{display_name} changed "
                                f"from {previous_value} "
                                f"to {current_value}."
                            ),
                    }
                )

        return changes

    # ======================================================
    # MAIN COMPARISON
    # ======================================================

    def compare(
        self,
        previous_decision,
        current_decision,
        trigger=None,
    ):

        trigger = trigger or {
            "type": "unspecified",
        }

        responder_changes = (
            self._compare_responder_states(
                previous_decision,
                current_decision,
            )
        )

        assignment_changes = (
            self._compare_assignments(
                previous_decision,
                current_decision,
            )
        )

        resource_changes = (
            self._compare_resources(
                previous_decision,
                current_decision,
            )
        )

        incident_changes = (
            self._compare_incident(
                previous_decision,
                current_decision,
            )
        )

        changes = (
            responder_changes
            + assignment_changes
            + resource_changes
            + incident_changes
        )

        material_types = {
            "network_reachability",
            "deployment_eligibility",
            "deployment_removed",
            "deployment_added",
            "resource_requirement",
            "incident_state",
        }

        material_changes = [
            change
            for change in changes
            if change.get("type")
            in material_types
        ]

        requires_replanning = bool(
            material_changes
        )

        previous_id = (
            previous_decision.get(
                "orchestration",
                {},
            ).get(
                "incident_id"
            )
        )

        current_id = (
            current_decision.get(
                "orchestration",
                {},
            ).get(
                "incident_id"
            )
        )

        if not changes:

            status = "stable"

        elif requires_replanning:

            status = (
                "replanning_completed"
            )

        else:

            status = "updated"

        return {
            "status":
                status,

            "requires_replanning":
                requires_replanning,

            "trigger":
                trigger,

            "previous_incident_id":
                previous_id,

            "current_incident_id":
                current_id,

            "change_count":
                len(changes),

            "material_change_count":
                len(material_changes),

            "changes":
                changes,

            "summary": {
                "responders_changed":
                    len(
                        responder_changes
                    ),

                "assignments_changed":
                    len(
                        assignment_changes
                    ),

                "resources_changed":
                    len(
                        resource_changes
                    ),

                "incident_changes":
                    len(
                        incident_changes
                    ),
            },
        }
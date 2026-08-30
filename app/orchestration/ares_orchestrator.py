from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone

from app.agents.disaster_assessment_agent import (
    DisasterAssessmentAgent,
)
from app.agents.responder_evaluator import (
    ResponderEvaluator,
)
from app.agents.response_planning_agent import (
    ResponsePlanningAgent,
)
from app.agents.operational_strategy_agent import (
    OperationalStrategyAgent,
)

from app.models.resources import DisasterZone


class ARESOrchestrator:

    def __init__(self):

        self.assessment_agent = (
            DisasterAssessmentAgent()
        )

        self.responder_evaluator = (
            ResponderEvaluator()
        )

        self.response_planning_agent = (
            ResponsePlanningAgent()
        )

        self.operational_strategy_agent = (
            OperationalStrategyAgent()
        )

    # ======================================================
    # SERIALIZATION
    # ======================================================

    @staticmethod
    def _serialize(value):

        if is_dataclass(value):
            return asdict(value)

        return value

    # ======================================================
    # DISASTER ZONE
    # ======================================================

    @staticmethod
    def _build_disaster_zone(
        incident,
        assessment,
    ):

        return DisasterZone(
            zone_id=(
                f"ZONE-{incident.incident_id}"
            ),

            name=(
                f"{assessment.severity.title()} "
                "Impact Zone"
            ),

            latitude=incident.latitude,
            longitude=incident.longitude,

            severity=(
                assessment.severity.lower()
            ),

            estimated_population=(
                assessment
                .estimated_population_exposed
            ),

            estimated_casualties=(
                assessment
                .estimated_casualties
            ),

            estimated_critical=(
                assessment
                .estimated_critical
            ),
        )

    # ======================================================
    # RESPONDER EVALUATION
    # ======================================================

    def evaluate_responders(
        self,
        responders,
        incident,
        offline_team_ids=None,
    ):

        offline_team_ids = set(
            offline_team_ids or []
        )

        evaluated_responders = []

        for responder in responders:

            network_evaluation = (
                self.responder_evaluator
                .evaluate_responder(
                    responder=responder,

                    disaster_latitude=(
                        incident.latitude
                    ),

                    disaster_longitude=(
                        incident.longitude
                    ),
                )
            )

            result = {
                "team_id":
                    responder.team_id,

                "name":
                    responder.name,

                "team_type":
                    responder.team_type,

                "members":
                    responder.members,

                "available":
                    responder.available,

                "phone_number":
                    responder.phone_number,

                **network_evaluation,
            }

            # ------------------------------------------
            # RUNTIME NETWORK OVERRIDE
            #
            # Used for live incident events such as
            # a communications outage.
            #
            # This is intentionally separate from:
            # responder.available
            #
            # because operational availability and
            # telecom reachability are different states.
            # ------------------------------------------

            if (
                responder.team_id
                in offline_team_ids
            ):

                result[
                    "reachable"
                ] = False

                result[
                    "connectivity"
                ] = []

                result[
                    "eligible_for_deployment"
                ] = False

                result[
                    "runtime_network_override"
                ] = True

                result[
                    "runtime_network_status"
                ] = "forced_unreachable"

            else:

                result[
                    "runtime_network_override"
                ] = False

                result[
                    "runtime_network_status"
                ] = None

            evaluated_responders.append(
                result
            )

        # ----------------------------------------------
        # RE-RANK AFTER RUNTIME OVERRIDES
        # ----------------------------------------------

        evaluated_responders.sort(
            key=lambda responder: (
                not responder[
                    "eligible_for_deployment"
                ],

                responder[
                    "distance_to_disaster_km"
                ],
            )
        )

        return evaluated_responders

    # ======================================================
    # CAMARA TOOL TRACE
    # ======================================================

    @staticmethod
    def build_tool_trace(
        evaluated_responders,
    ):

        tool_trace = []

        for responder in (
            evaluated_responders
        ):

            for tool_event in (
                responder.get(
                    "tool_trace",
                    [],
                )
            ):

                tool_trace.append(
                    {
                        "team_id":
                            responder[
                                "team_id"
                            ],

                        "team_name":
                            responder[
                                "name"
                            ],

                        **tool_event,
                    }
                )

        return tool_trace

    # ======================================================
    # RUNTIME EVENTS
    # ======================================================

    @staticmethod
    def build_runtime_events(
        evaluated_responders,
    ):

        events = []

        for responder in (
            evaluated_responders
        ):

            if responder.get(
                "runtime_network_override"
            ):

                events.append(
                    {
                        "type":
                            "network_outage",

                        "team_id":
                            responder[
                                "team_id"
                            ],

                        "team_name":
                            responder[
                                "name"
                            ],

                        "status":
                            "unreachable",

                        "message":
                            (
                                f"{responder['name']} "
                                "lost operational "
                                "network connectivity."
                            ),
                    }
                )

        return events

    # ======================================================
    # MAIN PIPELINE
    # ======================================================

    def run_incident(
        self,
        incident,
        responders,
        hospitals,
        relief_centers,
        offline_team_ids=None,
    ):

        started_at = datetime.now(
            timezone.utc
        )

        # ----------------------------------------------
        # 1. DISASTER ASSESSMENT
        # ----------------------------------------------

        assessment = (
            self.assessment_agent
            .assess_disaster(
                disaster_type=(
                    incident.disaster_type
                ),

                severity=(
                    incident.severity
                ),

                affected_radius_km=(
                    incident
                    .affected_radius_km
                ),

                population_density_per_km2=(
                    incident
                    .population_density_per_km2
                ),
            )
        )

        # ----------------------------------------------
        # 2. OPERATIONAL ZONE
        # ----------------------------------------------

        disaster_zone = (
            self._build_disaster_zone(
                incident=incident,
                assessment=assessment,
            )
        )

        # ----------------------------------------------
        # 3. NETWORK-AWARE RESPONDER ANALYSIS
        # ----------------------------------------------

        evaluated_responders = (
            self.evaluate_responders(
                responders=responders,

                incident=incident,

                offline_team_ids=(
                    offline_team_ids
                ),
            )
        )

        # ----------------------------------------------
        # 4. CAMARA TRACE
        # ----------------------------------------------

        tool_trace = (
            self.build_tool_trace(
                evaluated_responders
            )
        )

        camara_calls = sum(
            1
            for event in tool_trace
            if event.get(
                "invoked",
                False,
            )
        )

        successful_calls = sum(
            1
            for event in tool_trace
            if (
                event.get(
                    "invoked",
                    False,
                )
                and event.get(
                    "success",
                    False,
                )
            )
        )

        failed_calls = sum(
            1
            for event in tool_trace
            if (
                event.get(
                    "invoked",
                    False,
                )
                and not event.get(
                    "success",
                    False,
                )
            )
        )

        # ----------------------------------------------
        # 5. RUNTIME EVENTS
        # ----------------------------------------------

        runtime_events = (
            self.build_runtime_events(
                evaluated_responders
            )
        )

        # ----------------------------------------------
        # 6. RESPONSE PLAN
        # ----------------------------------------------

        response_plan = (
            self.response_planning_agent
            .generate_plan(
                disaster_zone=(
                    disaster_zone
                ),

                responders=(
                    evaluated_responders
                ),

                hospitals=hospitals,

                relief_centers=(
                    relief_centers
                ),
            )
        )

        # ----------------------------------------------
        # 7. OPERATIONAL STRATEGY
        # ----------------------------------------------

        operational_strategy = (
            self.operational_strategy_agent
            .generate_strategy(
                disaster_zone=(
                    disaster_zone
                ),

                response_plan=(
                    response_plan
                ),

                all_responders=(
                    evaluated_responders
                ),
            )
        )

        completed_at = datetime.now(
            timezone.utc
        )

        duration_ms = round(
            (
                completed_at
                - started_at
            ).total_seconds()
            * 1000,
            2,
        )

        # ==================================================
        # FINAL UNIFIED DECISION
        # ==================================================

        return {

            "orchestration": {

                "engine":
                    "ARES",

                "version":
                    "2.0",

                "status":
                    "completed",

                "incident_id":
                    incident.incident_id,

                "started_at":
                    started_at.isoformat(),

                "completed_at":
                    completed_at.isoformat(),

                "duration_ms":
                    duration_ms,
            },

            # ----------------------------------------------
            # AGENTIC / CAMARA
            # ----------------------------------------------

            "agentic_orchestration": {

                "policy": [

                    (
                        "Do not invoke telecom APIs "
                        "for responders already "
                        "marked unavailable."
                    ),

                    (
                        "Verify Device Reachability "
                        "before requesting responder "
                        "location."
                    ),

                    (
                        "Request Location Retrieval "
                        "only for network-reachable "
                        "responders."
                    ),

                    (
                        "Exclude responders when "
                        "communication availability "
                        "cannot be verified."
                    ),

                    (
                        "Use registered responder "
                        "coordinates as degraded "
                        "fallback if live location "
                        "retrieval fails."
                    ),

                    (
                        "Recalculate deployment "
                        "decisions when runtime "
                        "network state changes."
                    ),
                ],

                "camara_calls":
                    camara_calls,

                "successful_calls":
                    successful_calls,

                "failed_calls":
                    failed_calls,

                "tool_trace":
                    tool_trace,
            },

            # ----------------------------------------------
            # RUNTIME OPERATIONAL EVENTS
            # ----------------------------------------------

            "runtime_events":
                runtime_events,

            # ----------------------------------------------
            # INCIDENT
            # ----------------------------------------------

            "incident": {

                "incident_id":
                    incident.incident_id,

                "source":
                    incident.source,

                "timestamp":
                    incident.timestamp,

                "latitude":
                    incident.latitude,

                "longitude":
                    incident.longitude,

                "disaster_type":
                    incident.disaster_type,

                "severity":
                    incident.severity,

                "affected_radius_km":
                    incident
                    .affected_radius_km,

                "population_density_per_km2":
                    incident
                    .population_density_per_km2,

                "description":
                    incident.description,
            },

            "assessment":
                self._serialize(
                    assessment
                ),

            "disaster_zone":
                self._serialize(
                    disaster_zone
                ),

            "responders":
                evaluated_responders,

            "response_plan":
                response_plan,

            "operational_strategy":
                operational_strategy,
        }
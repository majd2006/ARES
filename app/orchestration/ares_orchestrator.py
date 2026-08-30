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
    """
    Central orchestration layer for ARES V2.

    Responsibilities:
    1. Assess an incident.
    2. Evaluate responder network availability.
    3. Orchestrate CAMARA API usage.
    4. Build an operational disaster zone.
    5. Generate a response plan.
    6. Generate an operational strategy.
    7. Return one unified decision object.
    """

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
    # INTERNAL HELPERS
    # ======================================================

    @staticmethod
    def _serialize(value):
        """
        Convert dataclass objects into JSON-friendly
        dictionaries when required.
        """

        if is_dataclass(value):
            return asdict(value)

        return value

    @staticmethod
    def _build_disaster_zone(
        incident,
        assessment,
    ):
        """
        Convert the disaster assessment into the
        DisasterZone model expected by downstream agents.
        """

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
    ):

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

            evaluated_responders.append(
                {
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
            )

        # --------------------------------------------------
        # RANK RESPONDERS
        #
        # Eligible responders appear first.
        # Within the same eligibility group,
        # nearest responders appear first.
        # --------------------------------------------------

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

        for responder in evaluated_responders:

            responder_trace = (
                responder.get(
                    "tool_trace",
                    [],
                )
            )

            for tool_event in responder_trace:

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
    # MAIN ORCHESTRATION PIPELINE
    # ======================================================

    def run_incident(
        self,
        incident,
        responders,
        hospitals,
        relief_centers,
    ):

        started_at = datetime.now(
            timezone.utc
        )

        # --------------------------------------------------
        # 1. DISASTER ASSESSMENT
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 2. CREATE OPERATIONAL DISASTER ZONE
        # --------------------------------------------------

        disaster_zone = (
            self._build_disaster_zone(
                incident=incident,
                assessment=assessment,
            )
        )

        # --------------------------------------------------
        # 3. NETWORK-AWARE RESPONDER EVALUATION
        # --------------------------------------------------

        evaluated_responders = (
            self.evaluate_responders(
                responders=responders,
                incident=incident,
            )
        )

        # --------------------------------------------------
        # 4. CAMARA ORCHESTRATION TRACE
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 5. RESPONSE PLANNING
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 6. OPERATIONAL STRATEGY
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 7. UNIFIED ARES DECISION
        # --------------------------------------------------

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

            # --------------------------------------------------
            # AGENTIC CAMARA ORCHESTRATION
            # --------------------------------------------------

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
                        "only for responders that are "
                        "network reachable."
                    ),

                    (
                        "Exclude responders when "
                        "communication availability "
                        "cannot be verified."
                    ),

                    (
                        "Use registered responder "
                        "coordinates as a degraded "
                        "fallback when Location "
                        "Retrieval fails."
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

            # --------------------------------------------------
            # INCIDENT
            # --------------------------------------------------

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

            # --------------------------------------------------
            # DISASTER ASSESSMENT
            # --------------------------------------------------

            "assessment":
                self._serialize(
                    assessment
                ),

            # --------------------------------------------------
            # OPERATIONAL ZONE
            # --------------------------------------------------

            "disaster_zone":
                self._serialize(
                    disaster_zone
                ),

            # --------------------------------------------------
            # RESPONDERS
            # --------------------------------------------------

            "responders":
                evaluated_responders,

            # --------------------------------------------------
            # RESPONSE PLAN
            # --------------------------------------------------

            "response_plan":
                response_plan,

            # --------------------------------------------------
            # OPERATIONAL STRATEGY
            # --------------------------------------------------

            "operational_strategy":
                operational_strategy,
        }
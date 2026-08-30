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
    Central orchestration layer for ARES.

    Responsibilities:
    1. Assess an incident.
    2. Evaluate responder network availability.
    3. Build an operational disaster zone.
    4. Generate a response plan.
    5. Generate an operational strategy.
    6. Return one unified decision object.

    Later V2 stages will extend this class with:
    - event-driven replanning
    - CAMARA tool selection
    - decision explanations
    - human approval state
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
        Convert the assessment result into the DisasterZone
        model expected by the planning/strategy agents.
        """

        return DisasterZone(
            zone_id=f"ZONE-{incident.incident_id}",
            name=f"{assessment.severity.title()} Impact Zone",
            latitude=incident.latitude,
            longitude=incident.longitude,
            severity=assessment.severity.lower(),
            estimated_population=(
                assessment.estimated_population_exposed
            ),
            estimated_casualties=(
                assessment.estimated_casualties
            ),
            estimated_critical=(
                assessment.estimated_critical
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
                self.responder_evaluator.evaluate_responder(
                    responder=responder,
                    disaster_latitude=incident.latitude,
                    disaster_longitude=incident.longitude,
                )
            )

            evaluated_responders.append(
                {
                    "team_id": responder.team_id,
                    "name": responder.name,
                    "team_type": responder.team_type,
                    "members": responder.members,
                    "available": responder.available,
                    "phone_number": responder.phone_number,

                    **network_evaluation,
                }
            )

        # Nearest eligible responders first.
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
            self.assessment_agent.assess_disaster(
                disaster_type=incident.disaster_type,
                severity=incident.severity,
                affected_radius_km=(
                    incident.affected_radius_km
                ),
                population_density_per_km2=(
                    incident.population_density_per_km2
                ),
            )
        )

        # --------------------------------------------------
        # 2. CREATE OPERATIONAL DISASTER ZONE
        # --------------------------------------------------

        disaster_zone = (
            self._build_disaster_zone(
                incident,
                assessment,
            )
        )

        # --------------------------------------------------
        # 3. NETWORK-AWARE RESPONDER EVALUATION
        # --------------------------------------------------

        evaluated_responders = (
            self.evaluate_responders(
                responders,
                incident,
            )
        )

        # --------------------------------------------------
        # 4. RESPONSE PLANNING
        # --------------------------------------------------

        response_plan = (
            self.response_planning_agent.generate_plan(
                disaster_zone=disaster_zone,
                responders=evaluated_responders,
                hospitals=hospitals,
                relief_centers=relief_centers,
            )
        )

        # --------------------------------------------------
        # 5. OPERATIONAL STRATEGY
        # --------------------------------------------------

        operational_strategy = (
            self.operational_strategy_agent.generate_strategy(
                disaster_zone=disaster_zone,
                response_plan=response_plan,
                all_responders=evaluated_responders,
            )
        )

        completed_at = datetime.now(
            timezone.utc
        )

        duration_ms = round(
            (
                completed_at - started_at
            ).total_seconds() * 1000,
            2,
        )

        # --------------------------------------------------
        # 6. UNIFIED ARES DECISION
        # --------------------------------------------------

        return {
            "orchestration": {
                "engine": "ARES",
                "version": "2.0",
                "status": "completed",
                "incident_id": incident.incident_id,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_ms": duration_ms,
            },

            "incident": {
                "incident_id": incident.incident_id,
                "source": incident.source,
                "timestamp": incident.timestamp,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "disaster_type": incident.disaster_type,
                "severity": incident.severity,
                "affected_radius_km": (
                    incident.affected_radius_km
                ),
                "population_density_per_km2": (
                    incident.population_density_per_km2
                ),
                "description": incident.description,
            },

            "assessment": (
                self._serialize(assessment)
            ),

            "disaster_zone": (
                self._serialize(disaster_zone)
            ),

            "responders": evaluated_responders,

            "response_plan": response_plan,

            "operational_strategy": (
                operational_strategy
            ),
        }
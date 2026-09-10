from app.agents.route_access_agent import (
    RouteAccessAgent,
)

from data.beirut_road_network import (
    beirut_road_corridors,
    get_responder_corridor_id,
)

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

        self.route_access_agent = (
            RouteAccessAgent(
                beirut_road_corridors
            )
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
        road_status_overrides=None,
        operational_location_mode="camara_preferred",
        geofence_status_by_team=None,
    ):

        offline_team_ids = set(
            offline_team_ids or []
        )

        road_status_overrides = (
            road_status_overrides or {}
        )

        geofence_status_by_team = (
            geofence_status_by_team or {}
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

                    operational_location_mode=(
                        operational_location_mode
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
            # ROUTE ACCESS INTELLIGENCE
            # ------------------------------------------

            if (
                operational_location_mode
                == "registered_scenario"
            ):

                corridor_id = (
                    get_responder_corridor_id(
                        responder.team_id
                    )
                )

                if corridor_id:

                    route_evaluation = (
                        self.route_access_agent
                        .evaluate_route(
                            corridor_id,

                            status_overrides=(
                                road_status_overrides
                            ),
                        )
                    )

                    result[
                        "route_access"
                    ] = route_evaluation

                    result[
                        "route_available"
                    ] = route_evaluation[
                        "route_available"
                    ]

                    result[
                        "route_decision"
                    ] = route_evaluation[
                        "route_decision"
                    ]

                    # ----------------------------------
                    # RUNTIME ROAD OVERRIDE METADATA
                    # ----------------------------------

                    result[
                        "runtime_route_override"
                    ] = (
                        corridor_id
                        in road_status_overrides
                    )

                    result[
                        "runtime_route_corridor_id"
                    ] = (
                        corridor_id
                        if corridor_id
                        in road_status_overrides
                        else None
                    )

                    result[
                        "runtime_route_status"
                    ] = (
                        road_status_overrides.get(
                            corridor_id
                        )
                        if corridor_id
                        in road_status_overrides
                        else None
                    )

                    if not route_evaluation[
                        "route_available"
                    ]:

                        result[
                            "eligible_for_deployment"
                        ] = False

                else:

                    result[
                        "route_access"
                    ] = None

                    result[
                        "route_available"
                    ] = True

                    result[
                        "route_decision"
                    ] = "unknown"

                    result[
                        "runtime_route_override"
                    ] = False

                    result[
                        "runtime_route_corridor_id"
                    ] = None

                    result[
                        "runtime_route_status"
                    ] = None

            else:

                result[
                    "route_access"
                ] = None

                result[
                    "route_available"
                ] = True

                result[
                    "route_decision"
                ] = "not_applicable"

                result[
                    "runtime_route_override"
                ] = False

                result[
                    "runtime_route_corridor_id"
                ] = None

                result[
                    "runtime_route_status"
                ] = None

            # ------------------------------------------
            # RUNTIME NETWORK OVERRIDE
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
            # ------------------------------------------
            # CAMARA GEOFENCING OPERATIONAL STATE
            # ------------------------------------------
            #
            # Geofencing is an independent operational
            # constraint. It does not modify network
            # reachability or route availability.
            #
            # Only an explicit "outside" state excludes
            # the responder. Initialization, unknown,
            # expired-subscription, or absent state does
            # not automatically remove a responder.
            # ------------------------------------------

            geofence_status = (
                geofence_status_by_team.get(
                    responder.team_id
                )
            )

            result[
                "geofence_status"
            ] = geofence_status

            result[
                "geofence_constraint_active"
            ] = (
                geofence_status
                == "outside"
            )

            result[
                "geofence_eligible"
            ] = (
                geofence_status
                != "outside"
            )

            if (
                geofence_status
                == "outside"
            ):

                result[
                    "eligible_for_deployment"
                ] = False

                result[
                    "geofence_exclusion_reason"
                ] = (
                    "CAMARA Geofencing reports "
                    "that the responder is outside "
                    "the designated operational zone."
                )

            else:

                result[
                    "geofence_exclusion_reason"
                ] = None

            evaluated_responders.append(
                result
            )

        # ----------------------------------------------
        # RE-RANK AFTER NETWORK + ROUTE ANALYSIS
        # ----------------------------------------------

        route_priority = {
            "direct": 0,
            "reroute": 1,
            "delayed": 2,
            "not_applicable": 0,
            "unknown": 3,
            "blocked": 4,
        }

        evaluated_responders.sort(
            key=lambda responder: (

                not responder[
                    "eligible_for_deployment"
                ],

                route_priority.get(
                    responder.get(
                        "route_decision",
                        "not_applicable",
                    ),
                    3,
                ),

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

            # ------------------------------------------
            # NETWORK EVENT
            # ------------------------------------------

            if responder.get(
                "runtime_network_override"
            ):

                events.append(
                    {
                        "type":
                            "network_outage",

                        "source": "live_demo_simulation",

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
                                f"Simulated network outage: {responder['name']} "
                                "is forced unreachable by the runtime demo override."
                            ),
                    }
                )

            # ------------------------------------------
            # ROAD ACCESS EVENT
            # ------------------------------------------

            if responder.get(
                "runtime_route_override"
            ):

                route_access = (
                    responder.get(
                        "route_access"
                    )
                    or {}
                )

                events.append(
                    {
                        "type":
                            "road_status_change",

                        "team_id":
                            responder[
                                "team_id"
                            ],

                        "team_name":
                            responder[
                                "name"
                            ],

                        "corridor_id":
                            responder.get(
                                "runtime_route_corridor_id"
                            ),

                        "corridor_name":
                            route_access.get(
                                "primary_corridor"
                            ),

                        "status":
                            responder.get(
                                "runtime_route_status"
                            ),

                        "route_decision":
                            responder.get(
                                "route_decision"
                            ),

                        "route_available":
                            responder.get(
                                "route_available"
                            ),

                        "message":
                            (
                                f"{route_access.get('primary_corridor')} "
                                "runtime road status changed "
                                f"to "
                                f"{responder.get('runtime_route_status')}. "
                                f"{responder['name']} route decision "
                                f"is now "
                                f"{responder.get('route_decision')}."
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
        road_status_overrides=None,
        operational_location_mode="camara_preferred",
        geofence_status_by_team=None,
        resource_pressure=False,
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
        # 3. NETWORK + ROUTE RESPONDER ANALYSIS
        # ----------------------------------------------

        evaluated_responders = (
            self.evaluate_responders(
                responders=responders,

                incident=incident,

                offline_team_ids=(
                    offline_team_ids
                ),

                road_status_overrides=(
                    road_status_overrides
                ),

                geofence_status_by_team=(
                    geofence_status_by_team
                ),

                operational_location_mode=(
                    operational_location_mode
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

        # Apply simulated reserve exhaustion before generating strategy.
        # The underlying relief-center dataset remains unchanged.
        if resource_pressure:
            response_plan["reserve_resources"]["ambulances"] = 0
            response_plan["reserve_resources"]["medical_teams"] = 0

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
                        "Skip Location Retrieval in Beirut; use "
                        "registered scenario coordinates."
                        if operational_location_mode == "registered_scenario"
                        else "Request Location Retrieval only for "
                        "network-reachable responders."
                    ),

                    (
                        "Exclude responders when "
                        "communication availability "
                        "cannot be verified."
                    ),

                    (
                        "Beirut coordinates are scenario-defined, "
                        "not Nokia simulator locations."
                        if operational_location_mode == "registered_scenario"
                        else "Use registered responder coordinates as degraded "
                        "fallback if live location retrieval fails."
                    ),

                    (
                        "Recalculate deployment "
                        "decisions when runtime "
                        "network or route state "
                        "changes."
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
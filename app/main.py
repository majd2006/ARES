from datetime import datetime

from flask import Flask, jsonify, render_template, request

from app.agents.incident_ingestion_agent import (
    IncidentIngestionAgent,
    IncidentInput,
)

from app.agents.disaster_assessment_agent import (
    DisasterAssessmentAgent,
)

from app.agents.incident_reassessment_agent import (
    IncidentReassessmentAgent,
)

from app.agents.staging_site_agent import (
    StagingSiteAgent,
)

from data.beirut_staging_sites import (
    beirut_staging_sites,
)

from app.agents.responder_evaluator import (
    ResponderEvaluator,
)

from app.agents.field_medical_post_agent import (
    FieldMedicalPostAgent,
)

from app.agents.response_planning_agent import (
    ResponsePlanningAgent,
)

from app.agents.operational_strategy_agent import (
    OperationalStrategyAgent,
)

from app.agents.resource_escalation_agent import (
    ResourceEscalationAgent,
)

from app.agents.regional_reinforcement_agent import (
    RegionalReinforcementAgent,
)

from app.models.resources import DisasterZone

from app.orchestration.command_approval import (
    CommandApprovalManager,
)

from app.orchestration.ares_orchestrator import (
    ARESOrchestrator,
)

from app.orchestration.decision_replanner import (
    DecisionReplanner,
)

from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
    regional_hospitals,
    regional_relief_centers,
)

from data.beirut_demo_scenario import (
    beirut_responder_teams,
    beirut_hospitals,
    beirut_relief_centers,
    beirut_regional_hospitals,
    beirut_regional_relief_centers,
    BEIRUT_PORT_LATITUDE,
    BEIRUT_PORT_LONGITUDE,
)

from data.beirut_road_network import (
    beirut_road_corridors,
)

app = Flask(__name__)


# ==========================================================
# AGENTS
# ==========================================================

ingestion_agent = IncidentIngestionAgent()
assessment_agent = DisasterAssessmentAgent()
reassessment_agent = IncidentReassessmentAgent()
field_medical_post_agent = FieldMedicalPostAgent()

evaluator = ResponderEvaluator()
planner = ResponsePlanningAgent()
strategy_agent = OperationalStrategyAgent()
escalation_agent = ResourceEscalationAgent()
regional_reinforcement_agent = RegionalReinforcementAgent()


# ==========================================================
# ARES V2 ORCHESTRATION
# ==========================================================

ares_orchestrator = ARESOrchestrator()
decision_replanner = DecisionReplanner()
command_approval_manager = CommandApprovalManager()
staging_site_agent = StagingSiteAgent(
    route_access_agent=ares_orchestrator.route_access_agent
)

# ==========================================================
# DEMO SCENARIO STATE
# ==========================================================

scenario_state = {
    "active": "standard",
}


def get_active_scenario():

    if scenario_state["active"] == "beirut":

        return {
            "scenario_id": "beirut",
            "title": (
                "Beirut Port Explosion — "
                "Historical Scenario"
            ),
            "scenario_type": "historical_demo",
            "location_name": "Beirut, Lebanon",

            "responders": (
                beirut_responder_teams
            ),
            "hospitals": (
                beirut_hospitals
            ),
            "relief_centers": (
                beirut_relief_centers
            ),
            "regional_hospitals": (
                beirut_regional_hospitals
            ),
            "regional_relief_centers": (
                beirut_regional_relief_centers
            ),

            "operational_location_mode": (
                "registered_scenario"
            ),

            "disclaimer": (
                "Historical Beirut Port scenario. "
                "Operational resources and assessment "
                "inputs are simulated for demonstration. "
                "Device network states are supplied "
                "through the Nokia/CAMARA simulator. "
                "ARES assessment values are prototype "
                "model estimates, not historical "
                "casualty data."
            ),
        }

    return {
        "scenario_id": "standard",
        "title": "ARES Standard Demo",
        "scenario_type": "live_demo",
        "location_name": "Network Simulator Scenario",

        "responders": responder_teams,
        "hospitals": hospitals,
        "relief_centers": relief_centers,
        "regional_hospitals": (
            regional_hospitals
        ),
        "regional_relief_centers": (
            regional_relief_centers
        ),

        "operational_location_mode": (
            "camara_preferred"
        ),

        "disclaimer": (
            "ARES standard demonstration scenario "
            "using Nokia/CAMARA simulator network "
            "services."
        ),
    }

def build_standard_demo_incident():

    return IncidentInput(
        incident_id="INC-001",
        source="simulated_satellite_alert",
        timestamp=(
            datetime.utcnow()
            .isoformat()
            + "Z"
        ),

        latitude=47.490,
        longitude=19.080,

        disaster_type="explosion",
        severity="critical",

        affected_radius_km=0.5,
        population_density_per_km2=2800,

        description=(
            "Baseline urban explosion scenario."
        ),
    )

def build_beirut_demo_incident():

    return IncidentInput(
        incident_id=(
            "BEIRUT-PORT-2020-DEMO"
        ),

        source=(
            "historical_demo_scenario"
        ),

        timestamp=(
            "2020-08-04T18:08:00+03:00"
        ),

        latitude=(
            BEIRUT_PORT_LATITUDE
        ),

        longitude=(
            BEIRUT_PORT_LONGITUDE
        ),

        disaster_type="explosion",
        severity="critical",

        affected_radius_km=0.5,

        # Prototype scenario assumption.
        # Not historical population data.
        population_density_per_km2=2800,

        description=(
            "Historical simulation inspired by "
            "the 4 August 2020 Beirut Port "
            "explosion. Operational resources "
            "and assessment inputs are simulated "
            "for demonstration."
        ),
    )
# ==========================================================
# ACTIVE INCIDENT
# ==========================================================

active_incident = IncidentInput(
    incident_id="INC-001",
    source="simulated_satellite_alert",
    timestamp="2026-08-20T18:00:00Z",

    latitude=47.490,
    longitude=19.080,

    disaster_type="explosion",
    severity="critical",

    affected_radius_km=0.5,
    population_density_per_km2=2800,

    description=(
        "Large explosion detected in a dense urban area."
    ),
)


# ==========================================================
# LIVE DEMO SIMULATION STATE
# ==========================================================

simulation_state = {
    "offline_teams": set(),

    # Runtime road-state changes.
    #
    # Example:
    # {
    #     "BR-05": "blocked"
    # }
    #
    # These overrides are transient demo events.
    # They do NOT modify the baseline Beirut road dataset.
    "road_status_overrides": {},

    "resource_pressure": False,
    "last_event": None,
}


# ==========================================================
# ARES V2 REPLANNING STATE
# ==========================================================

replanning_state = {
    "previous_decision": None,
    "current_decision": None,
    "last_result": None,
}


# ==========================================================
# INCIDENT REASSESSMENT STATE
# ==========================================================

reassessment_state = {
    "last_result": None,
}


# ==========================================================
# NOKIA GEOFENCING STATE
# ==========================================================

geofence_state = {
    "events": [],
    "team_status": {},
    "last_device_event": {},
}

def reset_transient_demo_state(
    event_type="demo_reset",
    message="ARES demo state reset.",
):

    simulation_state[
        "offline_teams"
    ].clear()

    simulation_state[
        "road_status_overrides"
    ].clear()

    simulation_state[
        "resource_pressure"
    ] = False

    simulation_state[
        "last_event"
    ] = {
        "type":
            event_type,

        "message":
            message,
    }

    replanning_state[
        "previous_decision"
    ] = None

    replanning_state[
        "current_decision"
    ] = None

    replanning_state[
        "last_result"
    ] = None

    reassessment_state[
        "last_result"
    ] = None

    geofence_state[
        "events"
    ].clear()

    geofence_state[
        "team_status"
    ].clear()

    geofence_state[
        "last_device_event"
    ].clear()

    command_approval_manager.reset()

# ==========================================================
# HELPERS
# ==========================================================

def parse_event_time(value):

    if not value:
        return None

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError:

        return None


# ==========================================================
# BUILD INCIDENT STATE
# ==========================================================

def build_incident_state():

    normalized_incident = ingestion_agent.ingest(
        active_incident
    )

    assessment = assessment_agent.assess_disaster(
        disaster_type=(
            normalized_incident.disaster_type
        ),

        severity=(
            normalized_incident.severity
        ),

        affected_radius_km=(
            normalized_incident.affected_radius_km
        ),

        population_density_per_km2=(
            normalized_incident
            .population_density_per_km2
        ),
    )

    disaster_zone = DisasterZone(
        zone_id=(
            normalized_incident.incident_id
        ),

        name="Active Disaster Zone",

        latitude=(
            normalized_incident.latitude
        ),

        longitude=(
            normalized_incident.longitude
        ),

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

    return (
        normalized_incident,
        assessment,
        disaster_zone,
    )


# ==========================================================
# BUILD DASHBOARD STATE
# ==========================================================

def build_dashboard_state():

    active_scenario = (
        get_active_scenario()
    )

    active_responders = (
        active_scenario["responders"]
    )

    active_hospitals = (
        active_scenario["hospitals"]
    )

    active_relief_centers = (
        active_scenario[
            "relief_centers"
        ]
    )

    active_regional_hospitals = (
        active_scenario[
            "regional_hospitals"
        ]
    )

    active_regional_relief_centers = (
        active_scenario[
            "regional_relief_centers"
        ]
    )

    operational_location_mode = (
        active_scenario[
            "operational_location_mode"
        ]
    )

    normalized_incident, assessment, zone = (
        build_incident_state()
    )

        # ======================================================
    # RESPONDER EVALUATION
    # ======================================================

    evaluated_responders = (
        ares_orchestrator.evaluate_responders(
            responders=active_responders,
            incident=normalized_incident,

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                simulation_state[
                    "road_status_overrides"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),
        )
    )

    # ======================================================
    # DASHBOARD-SPECIFIC STATE
    # ======================================================

    for responder in evaluated_responders:

        responder[
            "simulation_override"
        ] = responder.get(
            "runtime_network_override",
            False,
        )

    # ======================================================
    # ELIGIBLE RESPONDERS
    #
    # IMPORTANT:
    # Do not re-sort here by distance.
    # evaluate_responders() already applies the
    # authoritative ARES operational ranking:
    #
    # 1. deployment eligibility
    # 2. route quality
    # 3. physical distance
    # ======================================================

    eligible_responders = [
        responder
        for responder
        in evaluated_responders
        if responder.get(
            "eligible_for_deployment",
            False,
        )
    ]

    # ======================================================
    # RESPONDER RANKING
    # ======================================================

    for index, responder in enumerate(
        eligible_responders,
        start=1,
    ):

        responder[
            "rank"
        ] = index

    rank_lookup = {
        responder[
            "team_id"
        ]:
            responder[
                "rank"
            ]

        for responder
        in eligible_responders
    }

    for responder in evaluated_responders:

        responder[
            "rank"
        ] = (
            rank_lookup.get(
                responder[
                    "team_id"
                ]
            )
        )
    # ======================================================
    # PRIMARY RECOMMENDATION
    # ======================================================

    selected_team = (
        eligible_responders[0]
        if eligible_responders
        else None
    )

    responders_with_distance = [
        responder
        for responder
        in evaluated_responders
        if responder.get(
            "distance_to_disaster_km"
        )
        is not None
    ]

    closest_team = None

    if responders_with_distance:

        closest_team = min(
            responders_with_distance,

            key=lambda responder:
                responder[
                    "distance_to_disaster_km"
                ],
        )

    recommendation = {

        "selected_team":
            selected_team,

        "closest_team":
            closest_team,

        "network_affected_decision":
            (
                selected_team is not None
                and closest_team is not None
                and selected_team["team_id"]
                != closest_team["team_id"]
            ),
    }

    # ======================================================
    # RESPONSE PLAN
    # ======================================================

    response_plan = planner.generate_plan(
        disaster_zone=zone,
        responders=eligible_responders,
        hospitals=active_hospitals,
        relief_centers=(
            active_relief_centers
        ),
    )

    # ======================================================
    # SIMULATED LOCAL RESOURCE PRESSURE
    # ======================================================
    #
    # Demo-only operational event.
    #
    # This does not alter the underlying scenario resource
    # dataset. It represents a runtime condition in which
    # the locally mobilized ambulance and medical-team
    # reserves have become exhausted after deployment.
    #
    # ResourceEscalationAgent will independently detect the
    # exhausted reserves and determine whether regional
    # reinforcement is required.
    # ======================================================

    if simulation_state.get(
        "resource_pressure",
        False,
    ):
        response_plan[
            "reserve_resources"
        ]["ambulances"] = 0

        response_plan[
            "reserve_resources"
        ]["medical_teams"] = 0

        # ======================================================
    # FIELD MEDICAL POST
    # ======================================================

    field_medical_post = (
        field_medical_post_agent.evaluate(
            disaster_zone=zone,
            response_plan=response_plan,
            hospitals=active_hospitals,
            relief_centers=(
                active_relief_centers
            ),
        )
    )

        # ======================================================
    # SAFE STAGING SITE SELECTION
    # ======================================================

    if (
        active_scenario["scenario_id"] == "beirut"
        and
        field_medical_post.get(
            "required",
            False,
        )
    ):
        staging_site_selection = (
            staging_site_agent.evaluate_sites(
                incident=normalized_incident,
                sites=beirut_staging_sites,
                road_status_overrides=(
                    simulation_state[
                        "road_status_overrides"
                    ]
                ),
            )
        )
    else:
        staging_site_selection = {
            "status": "not_required",
            "minimum_safe_distance_km": 0.75,
            "selected_site": None,
            "evaluated_sites": [],
        }

    # ======================================================
    # RESOURCE ESCALATION
    # ======================================================

    resource_escalation = (
        escalation_agent.evaluate(
            response_plan=response_plan,
            hospitals=active_hospitals,
            relief_centers=(
                active_relief_centers
            ),
        )
    )
    # ======================================================
    # REGIONAL REINFORCEMENT
    # ======================================================

    regional_reinforcement = (
        regional_reinforcement_agent
        .generate_reinforcement_plan(

            disaster_zone=zone,

            resource_escalation=(
                resource_escalation
            ),

            hospitals=(
                active_regional_hospitals
            ),

            relief_centers=(
                active_regional_relief_centers
            ),
        )
    )

    # ======================================================
    # OPERATIONAL STRATEGY
    # ======================================================

    operational_strategy = (
        strategy_agent.generate_strategy(
           disaster_zone=zone,
           response_plan=response_plan,
           all_responders=(
               evaluated_responders
            ),
           field_medical_post=(
               field_medical_post
            ),
        )
    )

    # ======================================================
    # DEFAULT REASSESSMENT
    # ======================================================

    reassessment = (
        reassessment_state[
            "last_result"
        ]
        or
        {
            "status":
                "stable",

            "requires_replanning":
                False,

            "change_count":
                0,

            "changes":
                [],
        }
    )

        # ==========================================================
    # CAMARA / OPEN GATEWAY OBSERVABILITY
    # ==========================================================

    camara_trace = []

    camara_total_calls = 0
    camara_successful_calls = 0
    camara_failed_calls = 0
    camara_skipped_calls = 0

    for responder in evaluated_responders:

        responder_trace = (
            responder.get("tool_trace", [])
        )

        for tool_entry in responder_trace:

            invoked = tool_entry.get(
                "invoked",
                False,
            )

            success = tool_entry.get(
                "success"
            )

            if invoked:

                camara_total_calls += 1

                if success is True:
                    camara_successful_calls += 1

                elif success is False:
                    camara_failed_calls += 1

            else:
                camara_skipped_calls += 1

            camara_trace.append(
                {
                    "team_id":
                        responder.get(
                            "team_id"
                        ),

                    "team_name":
                        responder.get(
                            "name"
                        ),

                    "tool":
                        tool_entry.get(
                            "tool"
                        ),

                    "invoked":
                        invoked,

                    "success":
                        success,

                    "result":
                        tool_entry.get(
                            "result"
                        ),

                    "reason":
                        tool_entry.get(
                            "reason"
                        ),

                    "duration_ms":
                        tool_entry.get(
                            "duration_ms"
                        ),

                    "error":
                        tool_entry.get(
                            "error"
                        ),

                    "network_degraded":
                        responder.get(
                            "network_degraded",
                            False,
                        ),
                }
            )

    unreachable_responders = [
        responder
        for responder in evaluated_responders
        if responder.get("reachable") is False
        and not responder.get(
            "network_degraded",
            False,
        )
    ]

    nearest_unreachable = None

    if unreachable_responders:

        nearest_unreachable = min(
            unreachable_responders,
            key=lambda responder: (
                responder.get(
                    "distance_to_disaster_km"
                )
                if responder.get(
                    "distance_to_disaster_km"
                ) is not None
                else float("inf")
            ),
        )

    camara_observability = {
        "total_calls":
            camara_total_calls,

        "successful_calls":
            camara_successful_calls,

        "failed_calls":
            camara_failed_calls,

        "skipped_calls":
            camara_skipped_calls,

        "trace":
            camara_trace,

        "network_degraded":
            any(
                responder.get(
                    "network_degraded",
                    False,
                )
                for responder
                in evaluated_responders
            ),

        "decision_effect":
            (
                {
                    "team_id":
                        nearest_unreachable.get(
                            "team_id"
                        ),

                    "team_name":
                        nearest_unreachable.get(
                            "name"
                        ),

                    "distance_to_disaster_km":
                        nearest_unreachable.get(
                            "distance_to_disaster_km"
                        ),

                    "message":
                        (
                            f"{nearest_unreachable.get('name')} "
                            "was excluded from deployment because "
                            "CAMARA Device Reachability reported "
                            "the unit as unreachable."
                        ),
                }
                if nearest_unreachable
                else None
            ),
    }
    
    # ======================================================
    # RETURN DASHBOARD STATE
    # ======================================================

    return {

    # --------------------------------------------------
    # ACTIVE DEMO SCENARIO
    # --------------------------------------------------

        "scenario": {
        "scenario_id":
            active_scenario[
                "scenario_id"
            ],

        "title":
            active_scenario[
                "title"
            ],

        "scenario_type":
            active_scenario[
                "scenario_type"
            ],

        "location_name":
            active_scenario[
                "location_name"
            ],

        "operational_location_mode":
            operational_location_mode,

        "disclaimer":
            active_scenario[
                "disclaimer"
            ],
    },

    # --------------------------------------------------
    # ROAD NETWORK
    # --------------------------------------------------

    "road_network": (
        [
            {
                "corridor_id":
                    corridor.corridor_id,

                "name":
                    corridor.name,

                "status":
                    simulation_state[
                        "road_status_overrides"
                    ].get(
                        corridor.corridor_id,
                        corridor.status,
                    ),

                "baseline_status":
                    corridor.status,

                "runtime_override":
                    (
                        corridor.corridor_id
                        in simulation_state[
                            "road_status_overrides"
                        ]
                    ),

                "reason":
                    corridor.reason,

                "coordinates":
                    corridor.coordinates,

                "alternative_corridor_id":
                    corridor.alternative_corridor_id,
            }

            for corridor
            in beirut_road_corridors
        ]

        if active_scenario[
            "scenario_id"
        ] == "beirut"

        else []
    ),

    # --------------------------------------------------
    # INCIDENT
    # --------------------------------------------------

    "incident": {

        "incident_id":
            normalized_incident.incident_id,

        "zone_id":
            zone.zone_id,

        "name":
            zone.name,

        "source":
            normalized_incident.source,

        "timestamp":
            normalized_incident.timestamp,

        "description":
            normalized_incident.description,

        "disaster_type":
            normalized_incident.disaster_type,

        "latitude":
            zone.latitude,

        "longitude":
            zone.longitude,

        "severity":
            zone.severity,

        "affected_radius_km":
            assessment.affected_radius_km,

        "estimated_population":
            zone.estimated_population,

        "estimated_casualties":
            zone.estimated_casualties,

        "estimated_critical":
            zone.estimated_critical,
    },

    # --------------------------------------------------
    # IMPACT ZONES
    # --------------------------------------------------

    "impact_zones": [

        {
            "zone_name":
                impact_zone.zone_name,

            "inner_radius_km":
                impact_zone.inner_radius_km,

            "outer_radius_km":
                impact_zone.outer_radius_km,

            "area_km2":
                impact_zone.area_km2,

            "estimated_population":
                impact_zone.estimated_population,

            "estimated_casualties":
                impact_zone.estimated_casualties,

            "estimated_critical":
                impact_zone.estimated_critical,

            "casualty_rate":
                impact_zone.casualty_rate,

            "critical_rate":
                impact_zone.critical_rate,
        }

        for impact_zone
        in assessment.impact_zones
    ],

    # --------------------------------------------------
    # RESPONDERS
    # --------------------------------------------------

    "responders":
        evaluated_responders,

    # --------------------------------------------------
    # LOCAL HOSPITALS
    # --------------------------------------------------

    "hospitals": [

            {
                "hospital_id":
                    hospital
                    .hospital_id,

                "name":
                    hospital.name,

                "latitude":
                    hospital.latitude,

                "longitude":
                    hospital.longitude,

                "total_capacity":
                    hospital
                    .total_capacity,

                "available_capacity":
                    hospital
                    .available_capacity,
            }

            for hospital in active_hospitals
        ],

        # --------------------------------------------------
        # LOCAL RELIEF CENTERS
        # --------------------------------------------------

        "relief_centers": [

            {
                "center_id":
                    center
                    .center_id,

                "name":
                    center.name,

                "latitude":
                    center.latitude,

                "longitude":
                    center.longitude,

                "available_volunteers":
                    center
                    .available_volunteers,

                "available_medical_teams":
                    center
                    .available_medical_teams,

                "available_ambulances":
                    center
                    .available_ambulances,
            }

            for center
            in active_relief_centers
        ],

        # --------------------------------------------------
        # REGIONAL HOSPITALS
        # --------------------------------------------------

        "regional_hospitals": [

            {
                "hospital_id":
                    hospital
                    .hospital_id,

                "name":
                    hospital.name,

                "latitude":
                    hospital.latitude,

                "longitude":
                    hospital.longitude,

                "total_capacity":
                    hospital
                    .total_capacity,

                "available_capacity":
                    hospital
                    .available_capacity,
            }

            for hospital
            in active_regional_hospitals
        ],

        # --------------------------------------------------
        # REGIONAL RELIEF CENTERS
        # --------------------------------------------------

        "regional_relief_centers": [

            {
                "center_id":
                    center
                    .center_id,

                "name":
                    center.name,

                "latitude":
                    center.latitude,

                "longitude":
                    center.longitude,

                "available_volunteers":
                    center
                    .available_volunteers,

                "available_medical_teams":
                    center
                    .available_medical_teams,

                "available_ambulances":
                    center
                    .available_ambulances,
            }

            for center
            in active_regional_relief_centers
        ],

        # --------------------------------------------------
        # AI / DECISION STATE
        # --------------------------------------------------

        "recommendation":
            recommendation,

        "response_plan":
            response_plan,

        "resource_escalation":
            resource_escalation,

        "field_medical_post":
            field_medical_post,

        "staging_site_selection":
            staging_site_selection,

        "regional_reinforcement":
            regional_reinforcement,

        "operational_strategy":
            operational_strategy,

        "reassessment":
            reassessment,

            # --------------------------------------------------
        # CAMARA / OPEN GATEWAY OBSERVABILITY
        # --------------------------------------------------

        "camara_observability":
            camara_observability,
    
        # --------------------------------------------------
        # NOKIA GEOFENCING
        # --------------------------------------------------

        "geofencing": {

            "events":
                geofence_state[
                    "events"
                ],

            "team_status":
                geofence_state[
                    "team_status"
                ],
        },

        # --------------------------------------------------
        # LIVE SIMULATION
        # --------------------------------------------------

        "simulation": {

            "offline_teams":
                list(
                    simulation_state[
                        "offline_teams"
                    ]
                ),

            "last_event":
                simulation_state[
                    "last_event"
                ],
        },

        # --------------------------------------------------
        # ARES V2 DYNAMIC REPLANNING
        # --------------------------------------------------

        "dynamic_replanning": {

            "active":
                replanning_state[
                    "last_result"
                ] is not None,

            "result":
                replanning_state[
                    "last_result"
                ],

            "current_decision":
                replanning_state[
                    "current_decision"
                ],
        },
        "command_approval":
            command_approval_manager.get_state(),
    }


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html",
        state=build_dashboard_state(),
    )


# ==========================================================
# STATUS API
# ==========================================================

@app.route(
    "/api/status"
)
def api_status():

    return jsonify(
        build_dashboard_state()
    )


# ==========================================================
# INCIDENT INGESTION / UPDATE
# ==========================================================

@app.route(
    "/api/incidents",
    methods=["POST"],
)
def create_incident():

    global active_incident

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "JSON request body "
                        "is required."
                    ),
            }
        ), 400

    required_fields = [
        "incident_id",
        "source",
        "latitude",
        "longitude",
        "disaster_type",
        "severity",
        "affected_radius_km",
        "population_density_per_km2",
    ]

    missing_fields = [
        field
        for field
        in required_fields
        if field not in data
    ]

    if missing_fields:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    "Missing required fields.",

                "missing_fields":
                    missing_fields,
            }
        ), 400

    try:

        incoming_incident = IncidentInput(

            incident_id=
                data[
                    "incident_id"
                ],

            source=
                data[
                    "source"
                ],

            timestamp=
                data.get(
                    "timestamp",
                    "",
                ),

            latitude=
                float(
                    data[
                        "latitude"
                    ]
                ),

            longitude=
                float(
                    data[
                        "longitude"
                    ]
                ),

            disaster_type=
                data[
                    "disaster_type"
                ],

            severity=
                data[
                    "severity"
                ],

            affected_radius_km=
                float(
                    data[
                        "affected_radius_km"
                    ]
                ),

            population_density_per_km2=
                float(
                    data[
                        "population_density_per_km2"
                    ]
                ),

            description=
                data.get(
                    "description"
                ),
        )

        # ----------------------------------------------
        # VALIDATE / NORMALIZE
        # ----------------------------------------------

        normalized = (
            ingestion_agent.ingest(
                incoming_incident
            )
        )

        # ----------------------------------------------
        # CAPTURE PREVIOUS STATE
        # ----------------------------------------------

        previous_state = (
            build_dashboard_state()
        )

        previous_incident = (
            previous_state[
                "incident"
            ]
        )

        # ----------------------------------------------
        # UPDATE ACTIVE INCIDENT
        # ----------------------------------------------

        active_incident = (
            incoming_incident
        )

        # ----------------------------------------------
        # BUILD NEW STATE
        # ----------------------------------------------

        current_state = (
            build_dashboard_state()
        )

        current_incident = (
            current_state[
                "incident"
            ]
        )

        # ----------------------------------------------
        # INCIDENT REASSESSMENT
        # ----------------------------------------------

        reassessment_result = (
            reassessment_agent.compare(

                previous_incident=(
                    previous_incident
                ),

                current_incident=(
                    current_incident
                ),
            )
        )

        reassessment_state[
            "last_result"
        ] = reassessment_result

        if reassessment_result.get("requires_replanning"):

            command_approval_manager.register_new_decision(
                reason=(
                    "ARES generated a revised operational "
                    "decision after a material incident change."
                )
            )

        # Rebuild so reassessment is included

        current_state = (
            build_dashboard_state()
        )

        return jsonify(
            {
                "status":
                    "accepted",

                "incident": {

                    "incident_id":
                        normalized
                        .incident_id,

                    "disaster_type":
                        normalized
                        .disaster_type,

                    "severity":
                        normalized
                        .severity,

                    "latitude":
                        normalized
                        .latitude,

                    "longitude":
                        normalized
                        .longitude,

                    "affected_radius_km":
                        normalized
                        .affected_radius_km,

                    "ingestion_status":
                        normalized
                        .ingestion_status,
                },

                "reassessment":
                    reassessment_result,

                "message":
                    (
                        "Incident accepted. "
                        "ARES reassessed the "
                        "situation and recalculated "
                        "the operational response."
                    ),

                "dashboard_state":
                    current_state,
            }
        ), 201

    except ValueError as error:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    str(error),
            }
        ), 400

    except Exception as error:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "Incident processing "
                        "failed."
                    ),

                "details":
                    str(error),
            }
        ), 500


# ==========================================================
# NOKIA GEOFENCING WEBHOOK
# ==========================================================

@app.route(
    "/api/events/geofence",
    methods=["POST"],
)
def receive_geofence_event():

    event = request.get_json(
        silent=True
    )

    if not event:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "JSON event body "
                        "is required."
                    ),
            }
        ), 400

    # ======================================================
    # EXTRACT EVENT
    # ======================================================

    event_type = event.get(
        "type",
        ""
    )

    event_data = event.get(
        "data",
        {}
    )

    device = event_data.get(
        "device",
        {}
    )

    phone_number = (
        device.get(
            "phoneNumber"
        )
        or
        device.get(
            "phone_number"
        )
    )

    event_time_string = (
        event.get(
            "time"
        )
    )

    event_time = parse_event_time(
        event_time_string
    )

    # ======================================================
    # MATCH RESPONDER
    # ======================================================

    matched_team = None

    active_scenario = (
        get_active_scenario()
    )

    active_responders = (
        active_scenario[
            "responders"
        ]
    )

    for responder in active_responders:

        if (
            responder.phone_number
            == phone_number
        ):

            matched_team = responder

            break

    # ======================================================
    # RAW GEOFENCE STATUS
    # ======================================================

    if (
        "area-entered"
        in event_type
    ):

        raw_status = "inside"

    elif (
        "area-left"
        in event_type
    ):

        raw_status = "outside"

    elif (
        "subscription-ends"
        in event_type
    ):

        raw_status = (
            "subscription_ended"
        )

    else:

        raw_status = "unknown"

    # ======================================================
    # INITIALIZATION / DEBOUNCE
    # ======================================================

    final_status = raw_status

    initialization_pair = False

    previous_event = (
        geofence_state[
            "last_device_event"
        ].get(
            phone_number
        )
    )

    if (
        previous_event
        and event_time
        and previous_event.get(
            "time_object"
        )
    ):

        previous_status = (
            previous_event.get(
                "raw_status"
            )
        )

        previous_time = (
            previous_event.get(
                "time_object"
            )
        )

        time_difference = abs(
            (
                event_time
                - previous_time
            ).total_seconds()
        )

        opposite_pair = (
            (
                previous_status
                == "inside"
                and raw_status
                == "outside"
            )
            or
            (
                previous_status
                == "outside"
                and raw_status
                == "inside"
            )
        )

        # Nokia simulator can emit contradictory callbacks
        # immediately after subscription.
        # Treat these as initialization noise.

        if (
            opposite_pair
            and time_difference <= 3
        ):

            final_status = (
                "initializing"
            )

            initialization_pair = (
                True
            )

    # ======================================================
    # STORE RAW DEVICE EVENT
    # ======================================================

    geofence_state[
        "last_device_event"
    ][phone_number] = {

        "raw_status":
            raw_status,

        "time":
            event_time_string,

        "time_object":
            event_time,

        "subscription_id":
            event_data.get(
                "subscriptionId"
            ),
    }

    # ======================================================
    # STORE EVENT HISTORY
    # ======================================================

    stored_event = {

        "event_id":
            event.get(
                "id"
            ),

        "event_type":
            event_type,

        "time":
            event_time_string,

        "phone_number":
            phone_number,

        "team_id":
            (
                matched_team.team_id
                if matched_team
                else None
            ),

        "team_name":
            (
                matched_team.name
                if matched_team
                else None
            ),

        "raw_geofence_status":
            raw_status,

        "geofence_status":
            final_status,

        "initialization_pair":
            initialization_pair,

        "subscription_id":
            event_data.get(
                "subscriptionId"
            ),
    }

    geofence_state[
        "events"
    ].insert(
        0,
        stored_event
    )

    # Keep only latest 20 events

    geofence_state[
        "events"
    ] = (
        geofence_state[
            "events"
        ][:20]
    )

    # ======================================================
    # OPERATIONAL GEOFENCE STATE
    # ======================================================
    #
    # Only explicit geographic states are allowed to
    # influence deployment eligibility.
    #
    # "initializing", "unknown", and
    # "subscription_ended" are retained in event history
    # but do not modify the last trusted operational
    # geofence state.
    # ======================================================

    if not matched_team:

        return jsonify(
            {
                "status":
                    "received",

                "event":
                    stored_event,

                "replanning_triggered":
                    False,

                "message":
                    (
                        "Geofence event stored, but "
                        "the device could not be matched "
                        "to an active responder."
                    ),
            }
        ), 200

    team_id = (
        matched_team.team_id
    )

    team_name = (
        matched_team.name
    )

    previous_geofence_status = (
        geofence_state[
            "team_status"
        ].get(
            team_id
        )
    )

    actionable_status = (
        final_status
        in {
            "inside",
            "outside",
        }
    )

    # Non-operational callback states must never replace
    # the last trusted geographic state.

    if not actionable_status:

        return jsonify(
            {
                "status":
                    "received",

                "event":
                    stored_event,

                "replanning_triggered":
                    False,

                "message":
                    (
                        "Geofence event stored. "
                        "No operational geographic "
                        "state change was applied."
                    ),
            }
        ), 200

    # ======================================================
    # DETERMINE WHETHER ELIGIBILITY ACTUALLY CHANGES
    # ======================================================
    #
    # ARES operational policy:
    #
    # outside -> responder is geographically ineligible
    # inside  -> no geographic exclusion
    #
    # Therefore:
    #
    # None -> inside     = no eligibility change
    # inside -> inside   = no eligibility change
    # outside -> outside = no eligibility change
    # inside -> outside  = material change
    # None -> outside    = material change
    # outside -> inside  = material change
    # ======================================================

    previous_constraint_active = (
        previous_geofence_status
        == "outside"
    )

    current_constraint_active = (
        final_status
        == "outside"
    )

    operational_change = (
        previous_constraint_active
        != current_constraint_active
    )

    # ======================================================
    # NON-MATERIAL TRUSTED STATE UPDATE
    # ======================================================

    if not operational_change:

        geofence_state[
            "team_status"
        ][team_id] = final_status

        return jsonify(
            {
                "status":
                    "received",

                "event":
                    stored_event,

                "replanning_triggered":
                    False,

                "previous_geofence_status":
                    previous_geofence_status,

                "current_geofence_status":
                    final_status,

                "message":
                    (
                        "Trusted geofence state updated. "
                        "Responder deployment eligibility "
                        "did not materially change."
                    ),

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    # ======================================================
    # ACTIVE OPERATIONAL RESOURCES
    # ======================================================

    active_hospitals = (
        active_scenario[
            "hospitals"
        ]
    )

    active_relief_centers = (
        active_scenario[
            "relief_centers"
        ]
    )

    operational_location_mode = (
        active_scenario[
            "operational_location_mode"
        ]
    )

    # ======================================================
    # DECISION N — BEFORE GEOFENCE TRANSITION
    # ======================================================

    previous_geofence_state = dict(
        geofence_state[
            "team_status"
        ]
    )

    previous_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                simulation_state[
                    "road_status_overrides"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                previous_geofence_state
            ),

            resource_pressure=(
                simulation_state[
                    "resource_pressure"
                ]
            ),
        )
    )

    # ======================================================
    # APPLY TRUSTED GEOFENCE TRANSITION
    # ======================================================

    geofence_state[
        "team_status"
    ][team_id] = final_status

    # ======================================================
    # REGISTER OPERATIONAL EVENT
    # ======================================================

    if final_status == "outside":

        event_message = (
            f"{team_name} left the designated "
            "operational geofence."
        )

    else:

        event_message = (
            f"{team_name} re-entered the designated "
            "operational geofence."
        )

    operational_event = {
        "type":
            "geofence_transition",

        "source":
            "camara_geofencing_webhook",

        "team_id":
            team_id,

        "team_name":
            team_name,

        "previous_status":
            previous_geofence_status,

        "current_status":
            final_status,

        "timestamp":
            (
                event_time_string
                or datetime.utcnow()
                .isoformat()
                + "Z"
            ),

        "message":
            event_message,
    }

    simulation_state[
        "last_event"
    ] = operational_event

    # ======================================================
    # DECISION N+1 — AFTER GEOFENCE TRANSITION
    # ======================================================

    current_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                simulation_state[
                    "road_status_overrides"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=(
                simulation_state[
                    "resource_pressure"
                ]
            ),
        )
    )

    # ======================================================
    # EXPLAIN DECISION CHANGE
    # ======================================================

    replanning_result = (
        decision_replanner.compare(
            previous_decision=(
                previous_decision
            ),

            current_decision=(
                current_decision
            ),

            trigger={
                "type":
                    "geofence_transition",

                "team_id":
                    team_id,

                "team_name":
                    team_name,

                "previous_status":
                    previous_geofence_status,

                "current_status":
                    final_status,

                "source":
                    "camara_geofencing_webhook",
            },
        )
    )

    # ======================================================
    # STORE V2 REPLANNING STATE
    # ======================================================

    replanning_state[
        "previous_decision"
    ] = previous_decision

    replanning_state[
        "current_decision"
    ] = current_decision

    replanning_state[
        "last_result"
    ] = replanning_result

    # ======================================================
    # HUMAN-IN-THE-LOOP GOVERNANCE
    # ======================================================

    if replanning_result.get(
        "requires_replanning",
        False,
    ):

        command_approval_manager.register_new_decision(
            reason=(
                "ARES generated a revised operational "
                "decision after a CAMARA Geofencing "
                "state transition."
            )
        )

    # ======================================================
    # RESPONSE
    # ======================================================

    return jsonify(
        {
            "status":
                "accepted",

            "message":
                (
                    "CAMARA Geofencing state changed. "
                    "ARES evaluated the operational "
                    "impact and completed dynamic "
                    "replanning."
                ),

            "event":
                stored_event,

            "operational_event":
                operational_event,

            "previous_geofence_status":
                previous_geofence_status,

            "current_geofence_status":
                final_status,

            "replanning_triggered":
                replanning_result.get(
                    "requires_replanning",
                    False,
                ),

            "replanning":
                replanning_result,

            "decision": {
                "previous":
                    previous_decision,

                "current":
                    current_decision,
            },

            "dashboard_state":
                build_dashboard_state(),
        }
    ), 200


# ==========================================================
# SIMULATE NETWORK OUTAGE
# ==========================================================

@app.route(
    "/api/simulations/network-outage",
    methods=["POST"],
)
def simulate_network_outage():

    data = request.get_json(
        silent=True
    ) or {}

    team_id = data.get(
        "team_id"
    )

    # ======================================================
    # VALIDATION
    # ======================================================

    if not team_id:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    "team_id is required.",
            }
        ), 400

    active_scenario = (
        get_active_scenario()
    )

    active_responders = (
        active_scenario[
            "responders"
        ]
    )

    active_hospitals = (
        active_scenario[
            "hospitals"
        ]
    )

    active_relief_centers = (
        active_scenario[
            "relief_centers"
        ]
    )

    operational_location_mode = (
        active_scenario[
            "operational_location_mode"
        ]
    )

    responder_lookup = {
        responder.team_id:
            responder

        for responder
        in active_responders
    }

    if team_id not in responder_lookup:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "Unknown responder team: "
                        f"{team_id}"
                    ),
            }
        ), 404

    selected_responder = (
        responder_lookup[
            team_id
        ]
    )

    # ======================================================
    # DUPLICATE EVENT PROTECTION
    # ======================================================

    if (
        team_id
        in simulation_state[
            "offline_teams"
        ]
    ):

        return jsonify(
            {
                "status":
                    "already_offline",

                "message":
                    (
                        f"{team_id} is already "
                        "marked offline."
                    ),

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    # ======================================================
    # DECISION 1 — BEFORE NETWORK FAILURE
    # ======================================================

    previous_offline_teams = set(
        simulation_state[
            "offline_teams"
        ]
    )

    previous_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                previous_offline_teams
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=(
                simulation_state[
                    "resource_pressure"
                ]
            ),
            road_status_overrides=simulation_state["road_status_overrides"],
        )
    )
    # ======================================================
    # REGISTER NETWORK EVENT
    # ======================================================

    simulation_state[
        "offline_teams"
    ].add(
        team_id
    )

    event = {
        "type":
            "network_outage",

        "team_id":
            team_id,

        "team_name":
            selected_responder.name,

        "timestamp":
            datetime.utcnow()
            .isoformat()
            + "Z",

        "message":
            (
                f"{selected_responder.name} "
                "lost operational network "
                "connectivity."
            ),
    }

    simulation_state[
        "last_event"
    ] = event

    # ======================================================
    # DECISION 2 — AFTER NETWORK FAILURE
    # ======================================================

    current_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=(
                simulation_state[
                    "resource_pressure"
                ]
            ),
            road_status_overrides=simulation_state["road_status_overrides"],
        )
    )

    # ======================================================
    # EXPLAIN DECISION CHANGE
    # ======================================================

    replanning_result = (
        decision_replanner.compare(
            previous_decision=(
                previous_decision
            ),

            current_decision=(
                current_decision
            ),

            trigger={
                "type":
                    "network_outage",

                "team_id":
                    team_id,

                "team_name":
                    selected_responder.name,

                "source":
                    "live_demo_simulation",
            },
        )
    )

    # ======================================================
    # STORE V2 REPLANNING STATE
    # ======================================================

    replanning_state[
        "previous_decision"
    ] = previous_decision

    replanning_state[
        "current_decision"
    ] = current_decision

    replanning_state[
        "last_result"
    ] = replanning_result

    command_approval_manager.register_new_decision(
        reason=(
            "ARES generated a revised operational "
            "decision after a network outage."
        )
    )
    # ======================================================
    # RESPONSE
    # ======================================================

    return jsonify(
        {
            "status":
                "accepted",

            "message":
                (
                    "Network outage detected. "
                    "ARES completed dynamic "
                    "operational replanning."
                ),

            "event":
                event,

            "replanning":
                replanning_result,

            "decision": {

                "previous":
                    previous_decision,

                "current":
                    current_decision,
            },

            "dashboard_state":
                build_dashboard_state(),
        }
    ), 200


# ==========================================================
# SIMULATE ROAD OBSTRUCTION
# ==========================================================

@app.route(
    "/api/simulations/road-obstruction",
    methods=["POST"],
)
def simulate_road_obstruction():

    data = request.get_json(
        silent=True
    ) or {}

    corridor_id = (
        data.get("corridor_id")
        or "BR-05"
    )

    # ======================================================
    # SCENARIO VALIDATION
    # ======================================================

    active_scenario = (
        get_active_scenario()
    )

    scenario_id = (
        active_scenario
        .get(
            "scenario_id",
            "",
        )
    )

    operational_location_mode = (
        active_scenario[
            "operational_location_mode"
        ]
    )

    # Road-access intelligence is currently defined only
    # for the Beirut historical demonstration scenario.
    if (
        operational_location_mode
        != "registered_scenario"
    ):

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "Road obstruction simulation "
                        "is available only in the "
                        "Beirut scenario."
                    ),

                "scenario_id":
                    scenario_id,
            }
        ), 400

    # ======================================================
    # ROAD EVENT VALIDATION
    # ======================================================

    # BR-05 is intentionally used for the controlled demo
    # because B-R02 depends on it and no alternative
    # corridor is configured for that route.
    if corridor_id != "BR-05":

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "The controlled road-obstruction "
                        "demo currently supports BR-05."
                    ),
            }
        ), 400

    current_override = (
        simulation_state[
            "road_status_overrides"
        ].get(
            corridor_id
        )
    )

    if current_override == "blocked":

        return jsonify(
            {
                "status":
                    "already_blocked",

                "message":
                    (
                        f"{corridor_id} is already "
                        "blocked by the runtime "
                        "simulation."
                    ),

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    # ======================================================
    # ACTIVE OPERATIONAL RESOURCES
    # ======================================================

    active_responders = (
        active_scenario[
            "responders"
        ]
    )

    active_hospitals = (
        active_scenario[
            "hospitals"
        ]
    )

    active_relief_centers = (
        active_scenario[
            "relief_centers"
        ]
    )

    # ======================================================
    # DECISION 1 — BEFORE ROAD OBSTRUCTION
    # ======================================================

    previous_road_status_overrides = dict(
        simulation_state[
            "road_status_overrides"
        ]
    )

    previous_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                previous_road_status_overrides
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=(
                simulation_state[
                    "resource_pressure"
                ]
            ),
        )
    )

    # ======================================================
    # REGISTER ROAD EVENT
    # ======================================================

    simulation_state[
        "road_status_overrides"
    ][corridor_id] = "blocked"

    event = {
        "type":
            "road_obstruction",

        "corridor_id":
            corridor_id,

        "corridor_name":
            (
                "Pierre Gemayel / "
                "Corniche El Nahr"
            ),

        "affected_team_id":
            "B-R02",

        "affected_team_name":
            "Beirut Rescue Team Bravo",

        "previous_status":
            "open",

        "current_status":
            "blocked",

        "timestamp":
            datetime.utcnow()
            .isoformat()
            + "Z",

        "source":
            "live_demo_simulation",

        "message":
            (
                "A simulated obstruction blocked "
                "BR-05 Pierre Gemayel / Corniche "
                "El Nahr. ARES is re-evaluating "
                "responder accessibility."
            ),
    }

    simulation_state[
        "last_event"
    ] = event

    # ======================================================
    # DECISION 2 — AFTER ROAD OBSTRUCTION
    # ======================================================

    current_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                simulation_state[
                    "road_status_overrides"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=(
                simulation_state[
                    "resource_pressure"
                ]
            ),
        )
    )

    # ======================================================
    # EXPLAIN DECISION CHANGE
    # ======================================================

    replanning_result = (
        decision_replanner.compare(
            previous_decision=(
                previous_decision
            ),

            current_decision=(
                current_decision
            ),

            trigger={
                "type":
                    "road_obstruction",

                "corridor_id":
                    corridor_id,

                "corridor_name":
                    (
                        "Pierre Gemayel / "
                        "Corniche El Nahr"
                    ),

                "team_id":
                    "B-R02",

                "team_name":
                    "Beirut Rescue Team Bravo",

                "source":
                    "live_demo_simulation",
            },
        )
    )

    # ======================================================
    # STORE V2 REPLANNING STATE
    # ======================================================

    replanning_state[
        "previous_decision"
    ] = previous_decision

    replanning_state[
        "current_decision"
    ] = current_decision

    replanning_state[
        "last_result"
    ] = replanning_result

    # ======================================================
    # HUMAN-IN-THE-LOOP GOVERNANCE
    # ======================================================

    if replanning_result.get(
        "requires_replanning"
    ):

        command_approval_manager.register_new_decision(
            reason=(
                "ARES generated a revised operational "
                "decision after a simulated road "
                "obstruction changed responder "
                "accessibility."
            )
        )

    # ======================================================
    # RESPONSE
    # ======================================================

    return jsonify(
        {
            "status":
                "accepted",

            "message":
                (
                    "Road obstruction detected. "
                    "ARES completed dynamic "
                    "operational replanning."
                ),

            "event":
                event,

            "road_status_overrides":
                dict(
                    simulation_state[
                        "road_status_overrides"
                    ]
                ),

            "replanning":
                replanning_result,

            "decision": {

                "previous":
                    previous_decision,

                "current":
                    current_decision,
            },

            "command_approval":
                command_approval_manager
                .get_state(),

            "dashboard_state":
                build_dashboard_state(),
        }
    ), 200

# ==========================================================
# SIMULATE LOCAL RESOURCE PRESSURE
# ==========================================================

@app.route(
    "/api/simulations/resource-pressure",
    methods=["POST"],
)
def simulate_resource_pressure():

    # ======================================================
    # DUPLICATE EVENT PROTECTION
    # ======================================================

    if simulation_state.get(
        "resource_pressure",
        False,
    ):

        return jsonify(
            {
                "status":
                    "already_active",

                "message":
                    (
                        "Local resource pressure "
                        "is already active."
                    ),

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    # ======================================================
    # ACTIVE SCENARIO
    # ======================================================

    active_scenario = (
        get_active_scenario()
    )

    active_responders = (
        active_scenario[
            "responders"
        ]
    )

    active_hospitals = (
        active_scenario[
            "hospitals"
        ]
    )

    active_relief_centers = (
        active_scenario[
            "relief_centers"
        ]
    )

    operational_location_mode = (
        active_scenario[
            "operational_location_mode"
        ]
    )

    # ======================================================
    # DECISION 1 — BEFORE RESOURCE PRESSURE
    # ======================================================

    previous_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                simulation_state[
                    "road_status_overrides"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=False,
        )
    )

    # ======================================================
    # REGISTER RESOURCE-PRESSURE EVENT
    # ======================================================

    simulation_state[
        "resource_pressure"
    ] = True

    event = {
        "type":
            "resource_pressure",

        "timestamp":
            datetime.utcnow()
            .isoformat()
            + "Z",

        "source":
            "live_demo_simulation",

        "affected_resources": [
            "ambulances",
            "medical_teams",
        ],

        "message":
            (
                "Simulated operational pressure "
                "exhausted local ambulance and "
                "medical-team reserves. "
                "ARES is re-evaluating resource "
                "availability and regional "
                "reinforcement requirements."
            ),
    }

    simulation_state[
        "last_event"
    ] = event

    # ======================================================
    # DECISION 2 — AFTER RESOURCE PRESSURE
    # ======================================================

    current_decision = (
        ares_orchestrator.run_incident(
            incident=active_incident,

            responders=(
                active_responders
            ),

            hospitals=(
                active_hospitals
            ),

            relief_centers=(
                active_relief_centers
            ),

            offline_team_ids=(
                simulation_state[
                    "offline_teams"
                ]
            ),

            road_status_overrides=(
                simulation_state[
                    "road_status_overrides"
                ]
            ),

            operational_location_mode=(
                operational_location_mode
            ),

            geofence_status_by_team=(
                geofence_state[
                    "team_status"
                ]
            ),

            resource_pressure=True,
        )
    )

    # ======================================================
    # EXPLAIN DECISION CHANGE
    # ======================================================

    replanning_result = (
        decision_replanner.compare(
            previous_decision=(
                previous_decision
            ),

            current_decision=(
                current_decision
            ),

            trigger={
                "type":
                    "resource_pressure",

                "affected_resources": [
                    "ambulances",
                    "medical_teams",
                ],

                "source":
                    "live_demo_simulation",
            },
        )
    )

    # ======================================================
    # STORE V2 REPLANNING STATE
    # ======================================================

    replanning_state[
        "previous_decision"
    ] = previous_decision

    replanning_state[
        "current_decision"
    ] = current_decision

    replanning_state[
        "last_result"
    ] = replanning_result

    # ======================================================
    # HUMAN-IN-THE-LOOP GOVERNANCE
    # ======================================================

    command_approval_manager.register_new_decision(
        reason=(
            "ARES generated a revised operational decision after simulated "
            "resource pressure exhausted local reserves."
        )
    )

    # ======================================================
    # BUILD UPDATED OPERATIONAL STATE
    # ======================================================

    dashboard_state = (
        build_dashboard_state()
    )

    # ======================================================
    # RESPONSE
    # ======================================================

    return jsonify(
        {
            "status":
                "accepted",

            "event":
                event,

            "replanning":
                replanning_result,

            "resource_escalation":
                dashboard_state[
                    "resource_escalation"
                ],

            "regional_reinforcement":
                dashboard_state[
                    "regional_reinforcement"
                ],

            "command_approval":
                command_approval_manager
                .get_state(),

            "dashboard_state":
                dashboard_state,
        }
    ), 200
# ==========================================================
# RESET SIMULATION
# ==========================================================

@app.route(
    "/api/simulations/reset",
    methods=["POST"],
)
def reset_simulation():

    simulation_state[
        "offline_teams"
    ].clear()

    simulation_state[
        "road_status_overrides"
    ].clear()

    simulation_state[
        "resource_pressure"
    ] = False

    simulation_state[
        "last_event"
    ] = {

        "type":
            "simulation_reset",

        "message":
            (
                "Simulation reset. "
                "ARES returned to the "
                "Nokia baseline state."
            ),
    }

    # ======================================================
    # RESET ARES V2 REPLANNING STATE
    # ======================================================

    replanning_state[
        "previous_decision"
    ] = None

    replanning_state[
        "current_decision"
    ] = None

    replanning_state[
        "last_result"
    ] = None

    command_approval_manager.reset()

    return jsonify(
        {
            "status":
                "reset",

            "dashboard_state":
                build_dashboard_state(),
        }
    )


# ==========================================================
# RESET REASSESSMENT
# ==========================================================

@app.route(
    "/api/reassessment/reset",
    methods=["POST"],
)
def reset_reassessment():

    reassessment_state[
        "last_result"
    ] = None

    return jsonify(
        {
            "status":
                "reset",

            "reassessment": {

                "status":
                    "stable",

                "requires_replanning":
                    False,

                "change_count":
                    0,

                "changes":
                    [],
            },
        }
    )


# ==========================================================
# RESET GEOFENCING
# ==========================================================

@app.route(
    "/api/geofencing/reset",
    methods=["POST"],
)
def reset_geofencing():

    geofence_state[
        "events"
    ].clear()

    geofence_state[
        "team_status"
    ].clear()

    geofence_state[
        "last_device_event"
    ].clear()

    return jsonify(
        {
            "status":
                "reset",

            "geofencing": {

                "events":
                    [],

                "team_status":
                    {},
            },
        }
    )

# ==========================================================
# COMMAND APPROVAL
# ==========================================================

@app.route(
    "/api/command/approve",
    methods=["POST"],
)
def approve_command():

    data = request.get_json(
        silent=True
    ) or {}

    commander = (
        data.get("commander")
        or "Incident Commander"
    )

    notes = data.get(
        "notes"
    )

    decision_version = data.get(
        "decision_version"
    )

    try:

        result = (
            command_approval_manager.approve(
                commander=commander,
                notes=notes,
                decision_version=(
                    decision_version
                ),
            )
        )

        return jsonify(
            {
                "status":
                    "approved",

                "approval":
                    result,

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    except ValueError as error:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    str(error),

                "command_approval":
                    command_approval_manager
                    .get_state(),
            }
        ), 400


@app.route(
    "/api/command/reject",
    methods=["POST"],
)
def reject_command():

    data = request.get_json(
        silent=True
    ) or {}

    commander = (
        data.get("commander")
        or "Incident Commander"
    )

    notes = data.get(
        "notes"
    )

    decision_version = data.get(
        "decision_version"
    )

    try:

        result = (
            command_approval_manager.reject(
                commander=commander,
                notes=notes,
                decision_version=(
                    decision_version
                ),
            )
        )

        return jsonify(
            {
                "status":
                    "rejected",

                "approval":
                    result,

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    except ValueError as error:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    str(error),

                "command_approval":
                    command_approval_manager
                    .get_state(),
            }
        ), 400



    data = request.get_json(
        silent=True
    ) or {}

    commander = (
        data.get("commander")
        or "Incident Commander"
    )

    notes = data.get(
        "notes"
    )

    decision_version = data.get(
        "decision_version"
    )

    modifications = data.get(
        "modifications",
        {},
    )

    try:

        result = (
            command_approval_manager.modify(
                commander=commander,
                modifications=(
                    modifications
                ),
                notes=notes,
                decision_version=(
                    decision_version
                ),
            )
        )

        return jsonify(
            {
                "status":
                    "modified",

                "approval":
                    result,

                "dashboard_state":
                    build_dashboard_state(),
            }
        ), 200

    except ValueError as error:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    str(error),

                "command_approval":
                    command_approval_manager
                    .get_state(),
            }
        ), 400


@app.route(
    "/api/command/modify",
    methods=["POST"],
)
def modify_command():

    data = request.get_json(
        silent=True
    ) or {}

    commander = (
        data.get("commander")
        or "Incident Commander"
    )

    notes = data.get(
        "notes"
    )

    modifications = data.get(
        "modifications",
        {},
    )

    if not isinstance(
        modifications,
        dict,
    ):

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "modifications "
                        "must be a JSON object."
                    ),
            }
        ), 400

    result = (
        command_approval_manager.modify(
            commander=commander,
            modifications=modifications,
            notes=notes,
        )
    )

    return jsonify(
        {
            "status":
                "modified",

            "approval":
                result,

            "dashboard_state":
                build_dashboard_state(),
        }
    ), 200

# ==========================================================
# DEMO CONTROLLER
# ==========================================================

# ==========================================================
# DEMO SCENARIO SWITCHER
# ==========================================================

@app.route(
    "/api/demo/scenario",
    methods=["POST"],
)
def switch_demo_scenario():

    global active_incident

    data = request.get_json(
        silent=True
    ) or {}

    scenario_id = (
        data.get(
            "scenario_id"
        )
        or ""
    ).strip().lower()

    # ======================================================
    # VALIDATE SCENARIO
    # ======================================================

    if scenario_id not in {
        "standard",
        "beirut",
    }:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    (
                        "scenario_id must be "
                        "'standard' or 'beirut'."
                    ),
            }
        ), 400

    # ======================================================
    # ACTIVATE SCENARIO
    # ======================================================

    scenario_state[
        "active"
    ] = scenario_id

    if scenario_id == "beirut":

        active_incident = (
            build_beirut_demo_incident()
        )

        reset_message = (
            "ARES switched to the "
            "Beirut Port historical "
            "demonstration scenario."
        )

    else:

        active_incident = (
            build_standard_demo_incident()
        )

        reset_message = (
            "ARES switched to the "
            "standard Nokia/CAMARA "
            "demonstration scenario."
        )

    # ======================================================
    # CLEAR STALE OPERATIONAL STATE
    # ======================================================

    reset_transient_demo_state(
        event_type="scenario_switch",
        message=reset_message,
    )

    # ======================================================
    # BUILD CLEAN SCENARIO STATE
    # ======================================================

    dashboard_state = (
        build_dashboard_state()
    )

    return jsonify(
        {
            "status":
                "accepted",

            "scenario":
                dashboard_state[
                    "scenario"
                ],

            "message":
                reset_message,

            "dashboard_state":
                dashboard_state,
        }
    ), 200

@app.route(
    "/api/demo/reset",
    methods=["POST"],
)
def demo_reset():

    global active_incident

        # ======================================================
    # RESET ACTIVE SCENARIO INCIDENT
    # ======================================================

    if (
        scenario_state["active"]
        == "beirut"
    ):

        active_incident = (
            build_beirut_demo_incident()
        )

    else:

        active_incident = (
            build_standard_demo_incident()
        )

    # ======================================================
    # RESET NETWORK SIMULATION
    # ======================================================

    simulation_state[
        "offline_teams"
    ].clear()

    simulation_state[
        "road_status_overrides"
    ].clear()

    simulation_state[
        "resource_pressure"
    ] = False

    simulation_state[
        "last_event"
    ] = {
        "type":
            "demo_reset",

        "message":
            (
                "ARES demo state "
                "reset to baseline."
            ),
    }

    # ======================================================
    # RESET ARES V2 REPLANNING STATE
    # ======================================================

    replanning_state[
        "previous_decision"
    ] = None

    replanning_state[
        "current_decision"
    ] = None

    replanning_state[
        "last_result"
    ] = None

    # ======================================================
    # RESET REASSESSMENT
    # ======================================================

    reassessment_state[
        "last_result"
    ] = None

    # ======================================================
    # RESET GEOFENCING
    # ======================================================

    geofence_state[
        "events"
    ].clear()

    geofence_state[
        "team_status"
    ].clear()

    geofence_state[
        "last_device_event"
    ].clear()

    command_approval_manager.reset()
    
    return jsonify(
        {
            "status":
                "reset",

            "dashboard_state":
                build_dashboard_state(),
        }
    )


# ==========================================================
# DEMO BASELINE
# ==========================================================

@app.route(
    "/api/demo/baseline",
    methods=["POST"],
)
def demo_baseline():

    global active_incident

    previous_state = (
        build_dashboard_state()
    )

    active_incident = IncidentInput(
        incident_id="DEMO-BASELINE",
        source="simulated_satellite_alert",
        timestamp=(
            datetime.utcnow()
            .isoformat()
            + "Z"
        ),

        latitude=47.490,
        longitude=19.080,

        disaster_type="explosion",
        severity="critical",

        affected_radius_km=0.5,
        population_density_per_km2=2800,

        description=(
            "Initial urban explosion detected."
        ),
    )

    current_state = (
        build_dashboard_state()
    )

    reassessment_result = (
        reassessment_agent.compare(
            previous_incident=(
                previous_state[
                    "incident"
                ]
            ),

            current_incident=(
                current_state[
                    "incident"
                ]
            ),
        )
    )

    reassessment_state[
        "last_result"
    ] = reassessment_result

    return jsonify(
        {
            "status":
                "accepted",

            "message":
                (
                    "Baseline incident injected."
                ),

            "dashboard_state":
                build_dashboard_state(),
        }
    )


# ==========================================================
# DEMO ESCALATION
# ==========================================================

@app.route(
    "/api/demo/escalate",
    methods=["POST"],
)
def demo_escalate():

    global active_incident

    previous_state = (
        build_dashboard_state()
    )

    active_incident = IncidentInput(
        incident_id="DEMO-ESCALATED",
        source="simulated_satellite_alert",
        timestamp=(
            datetime.utcnow()
            .isoformat()
            + "Z"
        ),

        latitude=47.490,
        longitude=19.080,

        disaster_type="explosion",
        severity="critical",

        affected_radius_km=0.7,
        population_density_per_km2=3200,

        description=(
            "Incident footprint expanded "
            "with higher exposed population."
        ),
    )

    current_state = (
        build_dashboard_state()
    )

    reassessment_result = (
        reassessment_agent.compare(
            previous_incident=(
                previous_state[
                    "incident"
                ]
            ),

            current_incident=(
                current_state[
                    "incident"
                ]
            ),
        )
    )

    reassessment_state[
        "last_result"
    ] = reassessment_result

    if reassessment_result.get("requires_replanning"):

        command_approval_manager.register_new_decision(
            reason=(
                "ARES generated a revised operational "
                "decision after incident escalation."
            )
        )

    return jsonify(
        {
            "status":
                "accepted",

            "message":
                (
                    "Incident escalated. "
                    "ARES recalculated "
                    "the response."
                ),

            "reassessment":
                reassessment_result,

            "dashboard_state":
                build_dashboard_state(),
        }
    )


# ==========================================================
# START SERVER
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )

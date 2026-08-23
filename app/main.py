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

from app.agents.responder_evaluator import (
    ResponderEvaluator,
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

from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
    regional_hospitals,
    regional_relief_centers,
)


app = Flask(__name__)


# ==========================================================
# AGENTS
# ==========================================================

ingestion_agent = IncidentIngestionAgent()
assessment_agent = DisasterAssessmentAgent()
reassessment_agent = IncidentReassessmentAgent()

evaluator = ResponderEvaluator()
planner = ResponsePlanningAgent()
strategy_agent = OperationalStrategyAgent()
escalation_agent = ResourceEscalationAgent()
regional_reinforcement_agent = RegionalReinforcementAgent()


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
    "last_event": None,
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

    normalized_incident, assessment, zone = (
        build_incident_state()
    )

    # ======================================================
    # RESPONDER EVALUATION
    # ======================================================

    evaluated_responders = []

    for responder in responder_teams:

        try:

            result = evaluator.evaluate_responder(
                responder=responder,
                disaster_latitude=zone.latitude,
                disaster_longitude=zone.longitude,
            )

            result["team_id"] = responder.team_id
            result["name"] = responder.name
            result["team_type"] = responder.team_type
            result["members"] = responder.members

            # ----------------------------------------------
            # SIMULATED NETWORK OUTAGE
            # ----------------------------------------------

            if (
                responder.team_id
                in simulation_state["offline_teams"]
            ):

                result["reachable"] = False
                result["connectivity"] = []
                result[
                    "eligible_for_deployment"
                ] = False

                result[
                    "simulation_override"
                ] = True

            else:

                result[
                    "simulation_override"
                ] = False

            # ----------------------------------------------
            # GEOFENCE STATE
            # ----------------------------------------------

            result["geofence_status"] = (
                geofence_state[
                    "team_status"
                ].get(
                    responder.team_id
                )
            )

            evaluated_responders.append(
                result
            )

        except Exception as error:

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

                    "phone_number":
                        responder.phone_number,

                    "latitude":
                        responder.latitude,

                    "longitude":
                        responder.longitude,

                    "reachable":
                        False,

                    "connectivity":
                        [],

                    "distance_to_disaster_km":
                        None,

                    "eligible_for_deployment":
                        False,

                    "simulation_override":
                        (
                            responder.team_id
                            in simulation_state[
                                "offline_teams"
                            ]
                        ),

                    "geofence_status":
                        geofence_state[
                            "team_status"
                        ].get(
                            responder.team_id
                        ),

                    "error":
                        str(error),
                }
            )

    # ======================================================
    # ELIGIBLE RESPONDERS
    # ======================================================

    eligible_responders = [
        responder
        for responder in evaluated_responders
        if responder.get(
            "eligible_for_deployment",
            False,
        )
    ]

    eligible_responders.sort(
        key=lambda responder:
            responder[
                "distance_to_disaster_km"
            ]
    )

    # ======================================================
    # RESPONDER RANKING
    # ======================================================

    for index, responder in enumerate(
        eligible_responders,
        start=1,
    ):

        responder["rank"] = index

    rank_lookup = {
        responder["team_id"]:
            responder["rank"]

        for responder
        in eligible_responders
    }

    for responder in evaluated_responders:

        responder["rank"] = (
            rank_lookup.get(
                responder["team_id"]
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
        hospitals=hospitals,
        relief_centers=relief_centers,
    )

    # ======================================================
    # RESOURCE ESCALATION
    # ======================================================

    resource_escalation = (
        escalation_agent.evaluate(
            response_plan=response_plan,
            hospitals=hospitals,
            relief_centers=relief_centers,
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
                regional_hospitals
            ),

            relief_centers=(
                regional_relief_centers
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

    # ======================================================
    # RETURN DASHBOARD STATE
    # ======================================================

    return {

        # --------------------------------------------------
        # INCIDENT
        # --------------------------------------------------

        "incident": {

            "incident_id":
                normalized_incident
                .incident_id,

            "zone_id":
                zone.zone_id,

            "name":
                zone.name,

            "source":
                normalized_incident
                .source,

            "timestamp":
                normalized_incident
                .timestamp,

            "description":
                normalized_incident
                .description,

            "disaster_type":
                normalized_incident
                .disaster_type,

            "latitude":
                zone.latitude,

            "longitude":
                zone.longitude,

            "severity":
                zone.severity,

            "affected_radius_km":
                assessment
                .affected_radius_km,

            "estimated_population":
                zone
                .estimated_population,

            "estimated_casualties":
                zone
                .estimated_casualties,

            "estimated_critical":
                zone
                .estimated_critical,
        },

        # --------------------------------------------------
        # IMPACT ZONES
        # --------------------------------------------------

        "impact_zones": [

            {
                "zone_name":
                    impact_zone
                    .zone_name,

                "inner_radius_km":
                    impact_zone
                    .inner_radius_km,

                "outer_radius_km":
                    impact_zone
                    .outer_radius_km,

                "area_km2":
                    impact_zone
                    .area_km2,

                "estimated_population":
                    impact_zone
                    .estimated_population,

                "estimated_casualties":
                    impact_zone
                    .estimated_casualties,

                "estimated_critical":
                    impact_zone
                    .estimated_critical,

                "casualty_rate":
                    impact_zone
                    .casualty_rate,

                "critical_rate":
                    impact_zone
                    .critical_rate,
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

            for hospital in hospitals
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
            in relief_centers
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
            in regional_hospitals
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
            in regional_relief_centers
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

        "regional_reinforcement":
            regional_reinforcement,

        "operational_strategy":
            operational_strategy,

        "reassessment":
            reassessment,

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

    for responder in responder_teams:

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

        # Nokia simulator can emit
        # contradictory callbacks almost
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
    # UPDATE TEAM STATE
    # ======================================================

    if matched_team:

        geofence_state[
            "team_status"
        ][
            matched_team.team_id
        ] = final_status

    return jsonify(
        {
            "status":
                "received",

            "event":
                stored_event,
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

    if not team_id:

        return jsonify(
            {
                "status":
                    "error",

                "message":
                    "team_id is required.",
            }
        ), 400

    valid_team_ids = {
        responder.team_id
        for responder
        in responder_teams
    }

    if team_id not in valid_team_ids:

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

    simulation_state[
        "offline_teams"
    ].add(
        team_id
    )

    simulation_state[
        "last_event"
    ] = {

        "type":
            "network_outage",

        "team_id":
            team_id,

        "message":
            (
                f"{team_id} lost network "
                "connectivity. ARES "
                "automatically triggered "
                "responder replanning."
            ),
    }

    return jsonify(
        {
            "status":
                "accepted",

            "event":
                simulation_state[
                    "last_event"
                ],

            "dashboard_state":
                build_dashboard_state(),
        }
    )


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
# START SERVER
# ==========================================================

# ==========================================================
# DEMO CONTROLLER
# ==========================================================

@app.route(
    "/api/demo/reset",
    methods=["POST"],
)
def demo_reset():

    global active_incident

    # Reset active incident
    active_incident = IncidentInput(
        incident_id="INC-001",
        source="simulated_satellite_alert",
        timestamp=datetime.utcnow().isoformat() + "Z",

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

    # Reset network simulation
    simulation_state[
        "offline_teams"
    ].clear()

    simulation_state[
        "last_event"
    ] = {
        "type": "demo_reset",
        "message": (
            "ARES demo state reset to baseline."
        ),
    }

    # Reset reassessment
    reassessment_state[
        "last_result"
    ] = None

    # Reset geofencing state
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
            "status": "reset",
            "dashboard_state":
                build_dashboard_state(),
        }
    )


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
        timestamp=datetime.utcnow().isoformat() + "Z",

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
            previous_incident=
                previous_state["incident"],

            current_incident=
                current_state["incident"],
        )
    )

    reassessment_state[
        "last_result"
    ] = reassessment_result

    return jsonify(
        {
            "status": "accepted",
            "message": (
                "Baseline incident injected."
            ),
            "dashboard_state":
                build_dashboard_state(),
        }
    )


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
        timestamp=datetime.utcnow().isoformat() + "Z",

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
            previous_incident=
                previous_state["incident"],

            current_incident=
                current_state["incident"],
        )
    )

    reassessment_state[
        "last_result"
    ] = reassessment_result

    return jsonify(
        {
            "status": "accepted",
            "message": (
                "Incident escalated. "
                "ARES recalculated the response."
            ),
            "reassessment":
                reassessment_result,
            "dashboard_state":
                build_dashboard_state(),
        }
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
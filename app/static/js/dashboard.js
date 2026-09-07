/* =========================================================
   LOAD STATE
========================================================= */

const stateElement =
    document.getElementById(
        "ares-state"
    );

if (!stateElement) {
    throw new Error(
        "ARES state data was not found."
    );
}

const state =
    JSON.parse(
        stateElement.textContent
    );

const commandApproval =
    state.command_approval || {};

const currentDecisionVersion =
    commandApproval.decision_version;

const incident =
    state.incident;


/* =========================================================
   MAP
========================================================= */

const map =
    L.map(
        "map",
        {
            zoomControl: false
        }
    )
    .setView(
        [
            incident.latitude,
            incident.longitude
        ],
        14
    );


L.control
    .zoom(
        {
            position: "bottomright"
        }
    )
    .addTo(map);


L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution:
            "&copy; OpenStreetMap contributors",

        maxZoom:
            19
    }
).addTo(map);


/* =========================================================
   BEIRUT ROAD NETWORK
   ========================================================= */

if (
    Array.isArray(state.road_network)
    &&
    state.road_network.length > 0
) {

    const roadStyleByStatus = {
        open: {
            color: "#2dd4bf",
            weight: 5,
            opacity: 0.9,
            dashArray: null,
        },

        congested: {
            color: "#f6c453",
            weight: 5,
            opacity: 0.95,
            dashArray: "8 6",
        },

        blocked: {
            color: "#ff5a67",
            weight: 6,
            opacity: 0.95,
            dashArray: "4 6",
        },
    };


    state.road_network.forEach(
        (corridor) => {

            if (
                !Array.isArray(
                    corridor.coordinates
                )
                ||
                corridor.coordinates.length < 2
            ) {
                return;
            }

            const style = (
                roadStyleByStatus[
                    corridor.status
                ]
                ||
                {
                    color: "#9ca3af",
                    weight: 4,
                    opacity: 0.75,
                    dashArray: "6 6",
                }
            );

            const roadLine =
                L.polyline(
                    corridor.coordinates,
                    style
                )
                .addTo(map);

            const alternativeText = (
                corridor.alternative_corridor_id
                    ? `
                        <br>
                        <strong>
                            Alternative Corridor:
                        </strong>
                        ${corridor.alternative_corridor_id}
                    `
                    : ""
            );

            roadLine.bindPopup(`
                <div class="map-popup">
                    <strong>
                        ${corridor.name}
                    </strong>

                    <br>

                    Corridor:
                    ${corridor.corridor_id}

                    <br>

                    Status:
                    <strong>
                        ${corridor.status.toUpperCase()}
                    </strong>

                    <br><br>

                    ${corridor.reason}

                    ${alternativeText}
                </div>
            `);
        }
    );
}

/* =========================================================
   IMPACT ZONES
========================================================= */

const zoneStyles = [
    {
        color: "#ff5a67",
        fillColor: "#ff5a67",
        fillOpacity: 0.20
    },

    {
        color: "#f6c453",
        fillColor: "#f6c453",
        fillOpacity: 0.13
    },

    {
        color: "#56a8ff",
        fillColor: "#56a8ff",
        fillOpacity: 0.08
    }
];


const reversedZones =
    [...state.impact_zones]
    .reverse();


reversedZones.forEach(
    (zone, reverseIndex) => {

        const originalIndex =
            state.impact_zones.length
            - 1
            - reverseIndex;

        const style =
            zoneStyles[
                originalIndex
            ]
            || zoneStyles[2];

        const radiusMeters =
            zone.outer_radius_km
            * 1000;


        const circle =
            L.circle(
                [
                    incident.latitude,
                    incident.longitude
                ],
                {
                    radius:
                        radiusMeters,

                    color:
                        style.color,

                    fillColor:
                        style.fillColor,

                    fillOpacity:
                        style.fillOpacity,

                    weight:
                        2
                }
            )
            .addTo(map);


        circle.bindPopup(`
            <strong>
                ${zone.zone_name}
            </strong>

            <br><br>

            Radius:
            ${zone.inner_radius_km}
            -
            ${zone.outer_radius_km}
            km

            <br>

            Area:
            ${zone.area_km2}
            km²

            <br><br>

            Population:
            ${zone.estimated_population}

            <br>

            Casualties:
            ${zone.estimated_casualties}

            <br>

            Critical:
            ${zone.estimated_critical}
        `);
    }
);


/* =========================================================
   INCIDENT CENTER
========================================================= */

const incidentMarker =
    L.circleMarker(
        [
            incident.latitude,
            incident.longitude
        ],
        {
            radius:
                7,

            color:
                "#ffffff",

            fillColor:
                "#ff5a67",

            fillOpacity:
                1,

            weight:
                2
        }
    )
    .addTo(map);


incidentMarker.bindPopup(`
    <strong>
        ${incident.name}
    </strong>

    <br><br>

    Incident:
    ${incident.incident_id}

    <br>

    Type:
    ${incident.disaster_type}

    <br>

    Severity:
    ${incident.severity.toUpperCase()}

    <br><br>

    Population exposed:
    ${incident.estimated_population}

    <br>

    Estimated casualties:
    ${incident.estimated_casualties}

    <br>

    Critical casualties:
    ${incident.estimated_critical}
`);


/* =========================================================
   RESPONDERS
========================================================= */

state.responders.forEach(
    (responder) => {

        if (
            responder.latitude === null
            ||
            responder.longitude === null
            ||
            responder.latitude === undefined
            ||
            responder.longitude === undefined
        ) {
            return;
        }


        const markerColor =
            responder.reachable
                ? "#2dd4bf"
                : "#ff5a67";


        const marker =
            L.circleMarker(
                [
                    responder.latitude,
                    responder.longitude
                ],
                {
                    radius:
                        responder.rank === 1
                            ? 10
                            : 8,

                    color:
                        markerColor,

                    fillColor:
                        markerColor,

                    fillOpacity:
                        responder.reachable
                            ? 0.90
                            : 0.55,

                    weight:
                        responder.rank === 1
                            ? 3
                            : 2
                }
            )
            .addTo(map);


        const status =
            responder.reachable
                ? "REACHABLE"
                : "DISCONNECTED";


        const distance =
            responder.distance_to_disaster_km
                !== null
                &&
            responder.distance_to_disaster_km
                !== undefined

                ? `${responder.distance_to_disaster_km} km`

                : "Unavailable";


        const connectivity =
            responder.connectivity
            &&
            responder.connectivity.length > 0

                ? responder.connectivity.join(
                    " + "
                )

                : "None";


        const decision =
            responder.rank === 1
                ? "SELECTED"

                : responder.reachable
                    ? "STANDBY"

                    : "EXCLUDED";


        const zoneStatus =
            responder.geofence_status
            || "unknown";


        marker.bindPopup(`
            <strong>
                ${responder.team_id}
                ·
                ${responder.name}
            </strong>

            <br><br>

            Type:
            ${responder.team_type}

            <br>

            Personnel:
            ${responder.members}

            <br>

            Distance:
            ${distance}

            <br>

            Network:
            ${status}

            <br>

            Zone:
            ${zoneStatus.toUpperCase()}

            <br>

            Connectivity:
            ${connectivity}

            <br><br>

            Decision:
            ${decision}
        `);
    }
);


/* =========================================================
   HOSPITALS
========================================================= */

state.hospitals.forEach(
    (hospital) => {

        const marker =
            L.circleMarker(
                [
                    hospital.latitude,
                    hospital.longitude
                ],
                {
                    radius:
                        7,

                    color:
                        "#56a8ff",

                    fillColor:
                        "#56a8ff",

                    fillOpacity:
                        0.85,

                    weight:
                        2
                }
            )
            .addTo(map);


        marker.bindPopup(`
            <strong>
                ${hospital.name}
            </strong>

            <br><br>

            Available:
            ${hospital.available_capacity}

            <br>

            Total:
            ${hospital.total_capacity}
        `);
    }
);


/* =========================================================
   RELIEF CENTERS
========================================================= */

state.relief_centers.forEach(
    (center) => {

        const marker =
            L.circleMarker(
                [
                    center.latitude,
                    center.longitude
                ],
                {
                    radius:
                        7,

                    color:
                        "#f6c453",

                    fillColor:
                        "#f6c453",

                    fillOpacity:
                        0.85,

                    weight:
                        2
                }
            )
            .addTo(map);


        marker.bindPopup(`
            <strong>
                ${center.name}
            </strong>

            <br><br>

            Volunteers:
            ${center.available_volunteers}

            <br>

            Medical teams:
            ${center.available_medical_teams}

            <br>

            Ambulances:
            ${center.available_ambulances}
        `);
    }
);

/* =========================================================
   FIELD MEDICAL POST
========================================================= */

if (
    state.staging_site_selection &&
    state.staging_site_selection.selected_site
) {
    const site =
        state.staging_site_selection.selected_site;

    const fieldPostMarker =
        L.circleMarker(
            [
                site.latitude,
                site.longitude
            ],
            {
                radius: 9,
                color: "#ffffff",
                fillColor: "#2dd4bf",
                fillOpacity: 0.95,
                weight: 3
            }
        )
        .addTo(map);

    fieldPostMarker.bindPopup(`
        <div class="map-popup">
            <strong>
                ARES Field Medical Post
            </strong>

            <br><br>

            ${site.name}

            <br>

            Site ID:
            ${site.site_id}

            <br>

            Distance:
            ${site.distance_from_incident_km} km

            <br>

            Route:
            ${site.route_access.primary_corridor}

            <br>

            Access:
            ${site.route_decision.toUpperCase()}

            <br><br>

            <strong>
                SIMULATED ARES-SELECTED STAGING SITE
            </strong>
        </div>
    `);
}

/* =========================================================
   MAP BOUNDS
========================================================= */

const mapPoints = [
    [
        incident.latitude,
        incident.longitude
    ]
];


state.responders.forEach(
    (responder) => {

        if (
            responder.latitude !== null
            &&
            responder.longitude !== null
            &&
            responder.latitude !== undefined
            &&
            responder.longitude !== undefined
        ) {

            mapPoints.push(
                [
                    responder.latitude,
                    responder.longitude
                ]
            );
        }
    }
);


state.hospitals.forEach(
    (hospital) => {

        mapPoints.push(
            [
                hospital.latitude,
                hospital.longitude
            ]
        );
    }
);


state.relief_centers.forEach(
    (center) => {

        mapPoints.push(
            [
                center.latitude,
                center.longitude
            ]
        );
    }
);


if (
    Array.isArray(
        state.road_network
    )
) {

    state.road_network.forEach(
        (corridor) => {

            if (
                !Array.isArray(
                    corridor.coordinates
                )
            ) {
                return;
            }

            corridor.coordinates.forEach(
                (coordinate) => {

                    if (
                        Array.isArray(
                            coordinate
                        )
                        &&
                        coordinate.length === 2
                    ) {

                        mapPoints.push(
                            coordinate
                        );
                    }
                }
            );
        }
    );
}

if (
    state.staging_site_selection &&
    state.staging_site_selection.selected_site
) {
    const site =
        state.staging_site_selection.selected_site;

    mapPoints.push(
        [
            site.latitude,
            site.longitude
        ]
    );
}

if (mapPoints.length > 1) {

    map.fitBounds(
        L.latLngBounds(
            mapPoints
        ),
        {
            padding:
                [45, 45],

            maxZoom:
                14
        }
    );
}


/* =========================================================
   CAPACITY BARS
========================================================= */

document
    .querySelectorAll(
        ".capacity-fill"
    )
    .forEach(
        (element) => {

            const capacity =
                element.dataset.capacity;

            element.style.width =
                `${capacity}%`;
        }
    );


/* =========================================================
   INCIDENT CONTROL
========================================================= */

const injectIncidentButton =
    document.getElementById(
        "inject-incident-button"
    );

const incidentControlStatus =
    document.getElementById(
        "incident-control-status"
    );


function getInputValue(id) {

    const element =
        document.getElementById(id);

    return element
        ? element.value
        : "";
}


function showIncidentStatus(
    message,
    type
) {

    if (!incidentControlStatus) {
        return;
    }

    incidentControlStatus.textContent =
        message;

    incidentControlStatus.className =
        `incident-control-status ${type}`;
}


async function injectIncident() {

    if (!injectIncidentButton) {
        return;
    }

    injectIncidentButton.disabled =
        true;

    injectIncidentButton.textContent =
        "Processing...";

    try {

        const payload = {

            incident_id:
                getInputValue(
                    "incident-id"
                ),

            source:
                getInputValue(
                    "incident-source"
                ),

            timestamp:
                new Date()
                .toISOString(),

            latitude:
                Number(
                    getInputValue(
                        "incident-latitude"
                    )
                ),

            longitude:
                Number(
                    getInputValue(
                        "incident-longitude"
                    )
                ),

            disaster_type:
                getInputValue(
                    "disaster-type"
                ),

            severity:
                getInputValue(
                    "incident-severity"
                ),

            affected_radius_km:
                Number(
                    getInputValue(
                        "incident-radius"
                    )
                ),

            population_density_per_km2:
                Number(
                    getInputValue(
                        "population-density"
                    )
                ),

            description:
                getInputValue(
                    "incident-description"
                )
        };


        const response =
            await fetch(
                "/api/incidents",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message
                ||
                "Incident submission failed."
            );
        }


        showIncidentStatus(
            (
                "Incident accepted. "
                + "ARES is recalculating "
                + "the operational response..."
            ),
            "success"
        );


        setTimeout(
            () => {

                window.location.reload();

            },
            650
        );

    }

    catch (error) {

        showIncidentStatus(
            error.message,
            "error"
        );

        injectIncidentButton.disabled =
            false;

        injectIncidentButton.textContent =
            "Inject Incident";
    }
}


if (injectIncidentButton) {

    injectIncidentButton.addEventListener(
        "click",
        injectIncident
    );
}


/* =========================================================
   DYNAMIC REPLANNING
========================================================= */

const outageButton =
    document.getElementById(
        "simulate-outage-button"
    );

const resetSimulationButton =
    document.getElementById(
        "reset-simulation-button"
    );


async function simulateNetworkOutage() {

    if (!outageButton) {
        return;
    }

    outageButton.disabled =
        true;

    const originalText =
        outageButton.textContent;

    outageButton.textContent =
        "Simulating...";

    try {

        const scenarioId =
            state.scenario
                ? state.scenario.scenario_id
                : "standard";

        const targetTeamId =
            scenarioId === "beirut"
                ? "B-R01"
                : "R01";


        const response =
            await fetch(
                "/api/simulations/network-outage",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                team_id:
                                    targetTeamId
                            }
                        )
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message
                ||
                "Network outage simulation failed."
            );

        }


        setTimeout(
            () => {

                window.location.reload();

            },
            650
        );

    }

    catch (error) {

        alert(
            error.message
        );

        outageButton.disabled =
            false;

        outageButton.textContent =
            originalText;

    }

}


async function resetSimulation() {

    if (!resetSimulationButton) {
        return;
    }

    resetSimulationButton.disabled =
        true;

    resetSimulationButton.textContent =
        "Resetting...";

    try {

        const response =
            await fetch(
                "/api/simulations/reset",
                {
                    method:
                        "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Simulation reset failed."
            );
        }


        window.location.reload();

    }

    catch (error) {

        alert(
            error.message
        );

        resetSimulationButton.disabled =
            false;

        resetSimulationButton.textContent =
            "Reset Simulation";
    }
}


if (outageButton) {

    outageButton.addEventListener(
        "click",
        simulateNetworkOutage
    );
}


if (resetSimulationButton) {

    resetSimulationButton.addEventListener(
        "click",
        resetSimulation
    );
}


/* =========================================================
   MAP INVALIDATION
========================================================= */

window.addEventListener(
    "load",
    () => {

        setTimeout(
            () => {

                map.invalidateSize();

            },
            150
        );
    }
);
/* =========================================================
   DEMO CONTROLLER
========================================================= */

const demoStandardScenarioButton =
    document.getElementById(
        "demo-standard-scenario-button"
    );

const demoBeirutScenarioButton =
    document.getElementById(
        "demo-beirut-scenario-button"
    );

const demoResetButton =
    document.getElementById(
        "demo-reset-button"
    );

const demoBaselineButton =
    document.getElementById(
        "demo-baseline-button"
    );

const demoEscalateButton =
    document.getElementById(
        "demo-escalate-button"
    );

const demoNetworkButton =
    document.getElementById(
        "demo-network-button"
    );

if (demoNetworkButton) {

    const scenarioId =
        state.scenario
            ? state.scenario.scenario_id
            : "standard";

    demoNetworkButton.textContent =
        scenarioId === "beirut"
            ? "Simulate B-R01 Network Loss"
            : "Simulate R01 Network Loss";

}

if (demoNetworkButton) {

    const activeScenario =
        window.ARES_STATE
        &&
        window.ARES_STATE.scenario
            ? window.ARES_STATE.scenario
            : null;

    const scenarioId =
        activeScenario
            ? activeScenario.scenario_id
            : "standard";

    demoNetworkButton.textContent =
        scenarioId === "beirut"
            ? "Simulate B-R01 Network Loss"
            : "Simulate R01 Network Loss";

}

async function runDemoAction(
    button,
    url,
    body = null
) {

    if (!button) {
        return;
    }

    const originalText =
        button.textContent;

    button.disabled = true;
    button.textContent =
        "Processing...";

    try {

        const options = {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json"
            }
        };

        if (body !== null) {

            options.body =
                JSON.stringify(body);
        }


        const response =
            await fetch(
                url,
                options
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message
                ||
                "Demo action failed."
            );
        }


        setTimeout(
            () => {
                window.location.reload();
            },
            450
        );

    }

    catch (error) {

        alert(
            error.message
        );

        button.disabled =
            false;

        button.textContent =
            originalText;
    }
}

if (demoStandardScenarioButton) {

    demoStandardScenarioButton.addEventListener(
        "click",
        () => {

            runDemoAction(
                demoStandardScenarioButton,
                "/api/demo/scenario",
                {
                    scenario_id:
                        "standard"
                }
            );

        }
    );

}


if (demoBeirutScenarioButton) {

    demoBeirutScenarioButton.addEventListener(
        "click",
        () => {

            runDemoAction(
                demoBeirutScenarioButton,
                "/api/demo/scenario",
                {
                    scenario_id:
                        "beirut"
                }
            );

        }
    );

}

if (demoResetButton) {

    demoResetButton.addEventListener(
        "click",
        () => {

            runDemoAction(
                demoResetButton,
                "/api/demo/reset"
            );
        }
    );
}


if (demoBaselineButton) {

    demoBaselineButton.addEventListener(
        "click",
        () => {

            runDemoAction(
                demoBaselineButton,
                "/api/demo/baseline"
            );
        }
    );
}


if (demoEscalateButton) {

    demoEscalateButton.addEventListener(
        "click",
        () => {

            runDemoAction(
                demoEscalateButton,
                "/api/demo/escalate"
            );
        }
    );
}


if (demoNetworkButton) {

    demoNetworkButton.addEventListener(
        "click",
        () => {

            const scenarioId =
                state.scenario
                    ? state.scenario.scenario_id
                    : "standard";

            const targetTeamId =
                scenarioId === "beirut"
                    ? "B-R01"
                    : "R01";

            runDemoAction(
                demoNetworkButton,
                "/api/simulations/network-outage",
                {
                    team_id:
                        targetTeamId
                }
            );

        }
    );

}


/* =========================================================
   HUMAN-IN-THE-LOOP COMMAND AUTHORIZATION
========================================================= */

const approveCommandButton =
    document.getElementById(
        "approve-command-button"
    );

const modifyCommandButton =
    document.getElementById(
        "modify-command-button"
    );

const rejectCommandButton =
    document.getElementById(
        "reject-command-button"
    );

const confirmModificationButton =
    document.getElementById(
        "confirm-modification-button"
    );

const commandModificationPanel =
    document.getElementById(
        "command-modification-panel"
    );

const commandApprovalFeedback =
    document.getElementById(
        "command-approval-feedback"
    );


function getCommandInputValue(id) {

    const element =
        document.getElementById(id);

    return element
        ? element.value.trim()
        : "";
}


function showCommandFeedback(
    message,
    type
) {

    if (!commandApprovalFeedback) {
        return;
    }

    commandApprovalFeedback.textContent =
        message;

    commandApprovalFeedback.className =
        `command-approval-feedback ${type}`;
}


function setCommandButtonsDisabled(
    disabled
) {

    [
        approveCommandButton,
        modifyCommandButton,
        rejectCommandButton,
        confirmModificationButton
    ]
    .forEach(
        (button) => {

            if (button) {
                button.disabled =
                    disabled;
            }
        }
    );
}

function applyCommandAuthorizationState() {

    if (approveCommandButton) {
        approveCommandButton.disabled =
            commandApproval.can_approve !== true;
    }

    if (modifyCommandButton) {
        modifyCommandButton.disabled =
            commandApproval.can_modify !== true;
    }

    if (rejectCommandButton) {
        rejectCommandButton.disabled =
            commandApproval.can_reject !== true;
    }

    if (confirmModificationButton) {
        confirmModificationButton.disabled =
            commandApproval.can_modify !== true;
    }

    if (
        commandApproval.can_modify !== true
        &&
        commandModificationPanel
    ) {
        commandModificationPanel
            .classList
            .remove("open");
    }
}

applyCommandAuthorizationState();

async function submitCommandAction(
    url,
    payload,
    successMessage
) {

    setCommandButtonsDisabled(
        true
    );

    showCommandFeedback(
        "Recording command authorization...",
        "success"
    );

    try {

        const response =
            await fetch(
                url,
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message
                ||
                "Command authorization failed."
            );
        }


        showCommandFeedback(
            successMessage,
            "success"
        );


        setTimeout(
            () => {

                window.location.reload();

            },
            450
        );

    }

    catch (error) {

        showCommandFeedback(
            error.message,
            "error"
        );

        applyCommandAuthorizationState();
    }
}


if (approveCommandButton) {

    approveCommandButton.addEventListener(
        "click",
        () => {

            const commander =
                getCommandInputValue(
                    "commander-name"
                )
                ||
                "Incident Commander";

            const notes =
                getCommandInputValue(
                    "command-notes"
                );


            submitCommandAction(
                "/api/command/approve",

                {
    commander,

    notes:
        notes || null,

    decision_version:
        currentDecisionVersion
},

                "Operational plan authorized. Refreshing decision state..."
            );
        }
    );
}


if (rejectCommandButton) {

    rejectCommandButton.addEventListener(
        "click",
        () => {

            const commander =
                getCommandInputValue(
                    "commander-name"
                )
                ||
                "Incident Commander";

            const notes =
                getCommandInputValue(
                    "command-notes"
                );


            submitCommandAction(
                "/api/command/reject",

                {
    commander,

    notes:
        notes
        ||
        "Current recommendation rejected by incident command.",

    decision_version:
        currentDecisionVersion
},
                "Operational plan rejected. Refreshing decision state..."
            );
        }
    );
}


if (
    modifyCommandButton
    &&
    commandModificationPanel
) {

    modifyCommandButton.addEventListener(
        "click",
        () => {

            commandModificationPanel
                .classList
                .toggle(
                    "open"
                );

            if (
                commandModificationPanel
                .classList
                .contains(
                    "open"
                )
            ) {

                showCommandFeedback(
                    (
                        "Enter the commander adjustment, "
                        + "then confirm the modification."
                    ),
                    "success"
                );

            } else {

                commandApprovalFeedback.className =
                    "command-approval-feedback";

                commandApprovalFeedback.textContent =
                    "";
            }
        }
    );
}


if (confirmModificationButton) {

    confirmModificationButton.addEventListener(
        "click",
        () => {

            const commander =
                getCommandInputValue(
                    "commander-name"
                )
                ||
                "Incident Commander";

            const notes =
                getCommandInputValue(
                    "command-notes"
                );

            const priorityTeam =
                getCommandInputValue(
                    "modified-priority-team"
                );

            const instruction =
                getCommandInputValue(
                    "modified-instruction"
                );


            if (!priorityTeam) {

                showCommandFeedback(
                    "Select a reachable priority team.",
                    "error"
                );

                return;
            }


            if (!instruction) {

                showCommandFeedback(
                    "Enter an operational modification instruction.",
                    "error"
                );

                return;
            }


            submitCommandAction(
                "/api/command/modify",

                {
    commander,

    notes:
        notes
        ||
        "Commander-authorized operational modification.",

    decision_version:
        currentDecisionVersion,

    modifications: {
        priority_team:
            priorityTeam,

        instruction:
            instruction
    }
},
                

                "Commander modification recorded. Refreshing decision state..."
            );
        }
    );
}

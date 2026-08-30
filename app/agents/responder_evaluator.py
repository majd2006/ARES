from math import (
    radians,
    sin,
    cos,
    sqrt,
    atan2,
)

from app.agents.network_agent import (
    NetworkIntelligenceAgent,
)


class ResponderEvaluator:

    def __init__(self):

        self.network_agent = (
            NetworkIntelligenceAgent()
        )

    # ======================================================
    # DISTANCE
    # ======================================================

    @staticmethod
    def calculate_distance_km(
        lat1,
        lon1,
        lat2,
        lon2,
    ):

        earth_radius_km = 6371.0

        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return earth_radius_km * c

    # ======================================================
    # RESPONDER EVALUATION
    # ======================================================

    def evaluate_responder(
        self,
        responder,
        disaster_latitude: float,
        disaster_longitude: float,
    ):

        tool_trace = []

        # --------------------------------------------------
        # 1. LOCAL AVAILABILITY POLICY
        # --------------------------------------------------

        if not responder.available:

            tool_trace.append(
                {
                    "tool":
                        "CAMARA Device Reachability",

                    "invoked":
                        False,

                    "reason":
                        (
                            "Skipped because the "
                            "responder is already "
                            "marked unavailable."
                        ),

                    "result":
                        "not_required",
                }
            )

            tool_trace.append(
                {
                    "tool":
                        "CAMARA Location Retrieval",

                    "invoked":
                        False,

                    "reason":
                        (
                            "Skipped because the "
                            "responder is unavailable."
                        ),

                    "result":
                        "not_required",
                }
            )

            distance_km = (
                self.calculate_distance_km(
                    responder.latitude,
                    responder.longitude,
                    disaster_latitude,
                    disaster_longitude,
                )
            )

            return {
                "phone_number":
                    responder.phone_number,

                "reachable":
                    False,

                "connectivity":
                    [],

                "latitude":
                    responder.latitude,

                "longitude":
                    responder.longitude,

                "distance_to_disaster_km":
                    round(
                        distance_km,
                        2,
                    ),

                "eligible_for_deployment":
                    False,

                "location_source":
                    "registered_profile",

                "network_degraded":
                    False,

                "tool_trace":
                    tool_trace,
            }

        # --------------------------------------------------
        # 2. CAMARA DEVICE REACHABILITY
        # --------------------------------------------------

        reachability = (
            self.network_agent
            .check_responder_reachability(
                responder.phone_number
            )
        )

        tool_trace.append(
            {
                "tool":
                    "CAMARA Device Reachability",

                "invoked":
                    True,

                "reason":
                    (
                        "Verify that the responder "
                        "can receive operational "
                        "communications before "
                        "deployment."
                    ),

                "success":
                    reachability[
                        "api_success"
                    ],

                "result":
                    (
                        "reachable"
                        if reachability[
                            "reachable"
                        ]
                        else "unreachable"
                    ),

                "duration_ms":
                    reachability[
                        "duration_ms"
                    ],

                "error":
                    reachability[
                        "error"
                    ],
            }
        )

        # --------------------------------------------------
        # 3. CONDITIONAL LOCATION RETRIEVAL
        # --------------------------------------------------

        if reachability["reachable"]:

            location = (
                self.network_agent
                .get_responder_location(
                    responder.phone_number
                )
            )

            valid_api_location = (
                location["api_success"]
                and location["latitude"]
                is not None
                and location["longitude"]
                is not None
            )

            if valid_api_location:

                responder_latitude = (
                    location["latitude"]
                )

                responder_longitude = (
                    location["longitude"]
                )

                location_source = (
                    "camara_location_retrieval"
                )

            else:

                # Safe fallback to the registered
                # responder base/last known location.

                responder_latitude = (
                    responder.latitude
                )

                responder_longitude = (
                    responder.longitude
                )

                location_source = (
                    "registered_profile_fallback"
                )

            tool_trace.append(
                {
                    "tool":
                        "CAMARA Location Retrieval",

                    "invoked":
                        True,

                    "reason":
                        (
                            "Responder is reachable. "
                            "Retrieve current network "
                            "location to calculate "
                            "operational proximity."
                        ),

                    "success":
                        location[
                            "api_success"
                        ],

                    "result":
                        (
                            "location_received"
                            if valid_api_location
                            else "fallback_location_used"
                        ),

                    "duration_ms":
                        location[
                            "duration_ms"
                        ],

                    "error":
                        location[
                            "error"
                        ],
                }
            )

            location_api_failed = (
                not valid_api_location
            )

        else:

            # No point requesting deployment location
            # for a unit that cannot currently be
            # contacted.

            responder_latitude = (
                responder.latitude
            )

            responder_longitude = (
                responder.longitude
            )

            location_source = (
                "registered_profile"
            )

            location_api_failed = False

            tool_trace.append(
                {
                    "tool":
                        "CAMARA Location Retrieval",

                    "invoked":
                        False,

                    "reason":
                        (
                            "Skipped because Device "
                            "Reachability reported the "
                            "responder as unreachable."
                        ),

                    "result":
                        "not_required",
                }
            )

        # --------------------------------------------------
        # 4. DISTANCE
        # --------------------------------------------------

        distance_km = (
            self.calculate_distance_km(
                responder_latitude,
                responder_longitude,
                disaster_latitude,
                disaster_longitude,
            )
        )

        # --------------------------------------------------
        # 5. DEPLOYMENT ELIGIBILITY
        # --------------------------------------------------

        eligible = (
            responder.available
            and reachability[
                "reachable"
            ]
        )

        network_degraded = (
            not reachability[
                "api_success"
            ]
            or location_api_failed
        )

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        return {
            "phone_number":
                responder.phone_number,

            "reachable":
                reachability[
                    "reachable"
                ],

            "connectivity":
                reachability[
                    "connectivity"
                ],

            "latitude":
                responder_latitude,

            "longitude":
                responder_longitude,

            "distance_to_disaster_km":
                round(
                    distance_km,
                    2,
                ),

            "eligible_for_deployment":
                eligible,

            "location_source":
                location_source,

            "network_degraded":
                network_degraded,

            "tool_trace":
                tool_trace,
        }
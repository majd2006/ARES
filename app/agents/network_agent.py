import time

from app.network.nokia_client import (
    get_reachability_status,
    get_device_location,
)


class NetworkIntelligenceAgent:

    # ======================================================
    # DEVICE REACHABILITY
    # ======================================================

    def check_responder_reachability(
        self,
        phone_number: str,
    ):

        started_at = time.perf_counter()

        try:

            result = get_reachability_status(
                phone_number
            )

            # ------------------------------------------
            # RESPONSE VALIDATION
            # ------------------------------------------

            if not isinstance(
                result,
                dict,
            ):

                raise ValueError(
                    "Device Reachability returned "
                    "an invalid response."
                )

            if "reachable" not in result:

                raise ValueError(
                    "Device Reachability response "
                    "does not contain 'reachable'."
                )

            if not isinstance(
                result.get("reachable"),
                bool,
            ):

                raise ValueError(
                    "Device Reachability returned "
                    "an invalid reachable value."
                )

            duration_ms = round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            )

            return {
                "phone_number":
                    phone_number,

                "reachable":
                    result.get(
                        "reachable",
                        False,
                    ),

                "connectivity":
                    result.get(
                        "connectivity",
                        [],
                    ),

                "last_status_time":
                    result.get(
                        "lastStatusTime"
                    ),

                "api_success":
                    True,

                "api_name":
                    "Device Reachability",

                "duration_ms":
                    duration_ms,

                "error":
                    None,
            }

        except Exception as exc:

            duration_ms = round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            )

            # Fail closed:
            # if communication status cannot be verified,
            # ARES does not automatically deploy the unit.

            return {
                "phone_number":
                    phone_number,

                "reachable":
                    False,

                "connectivity":
                    [],

                "last_status_time":
                    None,

                "api_success":
                    False,

                "api_name":
                    "Device Reachability",

                "duration_ms":
                    duration_ms,

                "error":
                    str(exc),
            }

    # ======================================================
    # LOCATION RETRIEVAL
    # ======================================================

    def get_responder_location(
        self,
        phone_number: str,
    ):

        started_at = time.perf_counter()

        try:

            result = get_device_location(
                phone_number
            )

            # ------------------------------------------
            # RESPONSE VALIDATION
            # ------------------------------------------

            if not isinstance(
                result,
                dict,
            ):

                raise ValueError(
                    "Location Retrieval returned "
                    "an invalid response."
                )

            area = result.get(
                "area"
            )

            if not isinstance(
                area,
                dict,
            ):

                raise ValueError(
                    "Location Retrieval response "
                    "does not contain a valid area."
                )

            center = area.get(
                "center"
            )

            if not isinstance(
                center,
                dict,
            ):

                raise ValueError(
                    "Location Retrieval response "
                    "does not contain a valid center."
                )

            latitude = center.get(
                "latitude"
            )

            longitude = center.get(
                "longitude"
            )

            if (
                not isinstance(
                    latitude,
                    (int, float),
                )
                or
                not isinstance(
                    longitude,
                    (int, float),
                )
            ):

                raise ValueError(
                    "Location Retrieval returned "
                    "invalid coordinates."
                )

            if not (
                -90 <= latitude <= 90
                and
                -180 <= longitude <= 180
            ):

                raise ValueError(
                    "Location Retrieval returned "
                    "coordinates outside valid ranges."
                )

            duration_ms = round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            )

            return {
                "phone_number":
                    phone_number,

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "radius_m":
                    area.get(
                        "radius"
                    ),

                "area_type":
                    area.get(
                        "areaType"
                    ),

                "last_location_time":
                    result.get(
                        "lastLocationTime"
                    ),

                "api_success":
                    True,

                "api_name":
                    "Location Retrieval",

                "duration_ms":
                    duration_ms,

                "error":
                    None,
            }

        except Exception as exc:

            duration_ms = round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            )

            return {
                "phone_number":
                    phone_number,

                "latitude":
                    None,

                "longitude":
                    None,

                "radius_m":
                    None,

                "area_type":
                    None,

                "last_location_time":
                    None,

                "api_success":
                    False,

                "api_name":
                    "Location Retrieval",

                "duration_ms":
                    duration_ms,

                "error":
                    str(exc),
            }
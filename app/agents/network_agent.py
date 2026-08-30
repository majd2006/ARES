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

            area = result.get(
                "area",
                {},
            )

            center = area.get(
                "center",
                {},
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
                    center.get(
                        "latitude"
                    ),

                "longitude":
                    center.get(
                        "longitude"
                    ),

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
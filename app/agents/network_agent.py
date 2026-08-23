from app.network.nokia_client import (
    get_reachability_status,
    get_device_location,
)


class NetworkIntelligenceAgent:

    def check_responder_reachability(self, phone_number: str):
        result = get_reachability_status(phone_number)

        return {
            "phone_number": phone_number,
            "reachable": result.get("reachable", False),
            "connectivity": result.get("connectivity", []),
            "last_status_time": result.get("lastStatusTime"),
        }

    def get_responder_location(self, phone_number: str):
        result = get_device_location(phone_number)

        area = result.get("area", {})
        center = area.get("center", {})

        return {
            "phone_number": phone_number,
            "latitude": center.get("latitude"),
            "longitude": center.get("longitude"),
            "radius_m": area.get("radius"),
            "area_type": area.get("areaType"),
            "last_location_time": result.get("lastLocationTime"),
        }
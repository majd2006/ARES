from math import radians, sin, cos, sqrt, atan2

from app.agents.network_agent import NetworkIntelligenceAgent


class ResponderEvaluator:
    def __init__(self):
        self.network_agent = NetworkIntelligenceAgent()

    @staticmethod
    def calculate_distance_km(lat1, lon1, lat2, lon2):
        earth_radius_km = 6371.0

        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius_km * c

    def evaluate_responder(
        self,
        responder,
        disaster_latitude: float,
        disaster_longitude: float,
    ):
        reachability = self.network_agent.check_responder_reachability(
            responder.phone_number
        )

        distance_km = self.calculate_distance_km(
            responder.latitude,
            responder.longitude,
            disaster_latitude,
            disaster_longitude,
        )

        eligible = (
            responder.available
            and reachability["reachable"]
        )

        return {
            "phone_number": responder.phone_number,
            "reachable": reachability["reachable"],
            "connectivity": reachability["connectivity"],
            "latitude": responder.latitude,
            "longitude": responder.longitude,
            "distance_to_disaster_km": round(distance_km, 2),
            "eligible_for_deployment": eligible,
        }
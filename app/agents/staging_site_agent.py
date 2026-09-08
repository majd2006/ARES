from math import radians, sin, cos, sqrt, atan2


class StagingSiteAgent:

    def __init__(
        self,
        route_access_agent,
    ):
        self.route_access_agent = (
            route_access_agent
        )

    @staticmethod
    def _distance_km(
        lat1,
        lon1,
        lat2,
        lon2,
    ):
        earth_radius_km = 6371.0

        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        delta_lat = (
            lat2_rad - lat1_rad
        )

        delta_lon = (
            lon2_rad - lon1_rad
        )

        a = (
            sin(delta_lat / 2) ** 2
            +
            cos(lat1_rad)
            * cos(lat2_rad)
            * sin(delta_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return earth_radius_km * c

    def evaluate_sites(
        self,
        incident,
        sites,
        minimum_safe_distance_km=0.75,
        road_status_overrides=None,
    ):
        road_status_overrides = (
            road_status_overrides or {}
        )
        evaluated = []

        for site in sites:

            distance_km = self._distance_km(
                incident.latitude,
                incident.longitude,
                site.latitude,
                site.longitude,
            )

            route = (
                self.route_access_agent
                .evaluate_route(
                    site.corridor_id,
                    status_overrides=(
                        road_status_overrides
                    ),
                )
            )

            outside_impact_zone = (
                distance_km
                >
                incident.affected_radius_km
            )

            meets_safety_buffer = (
                distance_km
                >= minimum_safe_distance_km
            )

            route_available = (
                route.get(
                    "route_available",
                    False,
                )
            )

            eligible = (
                outside_impact_zone
                and
                meets_safety_buffer
                and
                route_available
            )

            route_decision = route.get(
                "route_decision",
                "blocked",
            )

            route_score = {
                "direct": 0,
                "reroute": 1,
                "delayed": 2,
                "blocked": 3,
            }.get(
                route_decision,
                3,
            )

            evaluated.append(
                {
                    "site_id":
                        site.site_id,

                    "name":
                        site.name,

                    "latitude":
                        site.latitude,

                    "longitude":
                        site.longitude,

                    "corridor_id":
                        site.corridor_id,

                    "site_type":
                        site.site_type,

                    "distance_from_incident_km":
                        round(
                            distance_km,
                            2,
                        ),

                    "outside_impact_zone":
                        outside_impact_zone,

                    "meets_safety_buffer":
                        meets_safety_buffer,

                    "route_available":
                        route_available,

                    "route_decision":
                        route_decision,

                    "route_access":
                        route,

                    "eligible":
                        eligible,

                    "notes":
                        site.notes,

                    "_route_score":
                        route_score,
                }
            )

        evaluated.sort(
            key=lambda site: (
                not site["eligible"],
                site["_route_score"],
                site[
                    "distance_from_incident_km"
                ],
            )
        )

        for site in evaluated:
            site.pop(
                "_route_score",
                None,
            )

        eligible_sites = [
            site
            for site in evaluated
            if site["eligible"]
        ]

        selected_site = (
            eligible_sites[0]
            if eligible_sites
            else None
        )

        return {
            "status": (
                "site_selected"
                if selected_site
                else "no_safe_site_available"
            ),
            "minimum_safe_distance_km":
                minimum_safe_distance_km,
            "selected_site":
                selected_site,
            "evaluated_sites":
                evaluated,
        }
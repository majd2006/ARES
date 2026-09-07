from typing import Dict, List

from data.beirut_road_network import (
    RoadCorridor,
)


class RouteAccessAgent:

    def __init__(
        self,
        road_corridors: List[RoadCorridor],
    ):

        self.road_corridors = {
            corridor.corridor_id: corridor
            for corridor in road_corridors
        }


    def evaluate_route(
        self,
        primary_corridor_id: str,
    ) -> Dict:

        corridor = self.road_corridors.get(
            primary_corridor_id
        )

        if corridor is None:

            return {
                "route_available": False,
                "primary_corridor_id":
                    primary_corridor_id,
                "primary_corridor": None,
                "primary_status": "unknown",
                "alternative_corridor": None,
                "alternative_status": None,
                "route_decision": "blocked",
                "reason": (
                    "Primary corridor is not "
                    "defined in the active road "
                    "network."
                ),
            }


        status = corridor.status.lower()


        if status == "open":

            return {
                "route_available": True,
                "primary_corridor_id":
                    corridor.corridor_id,
                "primary_corridor":
                    corridor.name,
                "primary_status":
                    corridor.status,
                "alternative_corridor":
                    None,
                "alternative_status":
                    None,
                "route_decision":
                    "direct",
                "reason":
                    corridor.reason,
            }


        if status == "congested":

            return {
                "route_available": True,
                "primary_corridor_id":
                    corridor.corridor_id,
                "primary_corridor":
                    corridor.name,
                "primary_status":
                    corridor.status,
                "alternative_corridor":
                    None,
                "alternative_status":
                    None,
                "route_decision":
                    "delayed",
                "reason":
                    corridor.reason,
            }


        if status == "blocked":

            alternative = None

            if corridor.alternative_corridor_id:

                alternative = (
                    self.road_corridors.get(
                        corridor
                        .alternative_corridor_id
                    )
                )


            if (
                alternative
                and
                alternative.status.lower()
                in {
                    "open",
                    "congested",
                }
            ):

                return {
                    "route_available": True,
                    "primary_corridor_id":
                        corridor.corridor_id,
                    "primary_corridor":
                        corridor.name,
                    "primary_status":
                        corridor.status,
                    "alternative_corridor":
                        alternative.name,
                    "alternative_status":
                        alternative.status,
                    "route_decision":
                        "reroute",
                    "reason": (
                        f"{corridor.name} is "
                        f"blocked. "
                        f"ARES selected "
                        f"{alternative.name} "
                        f"as an alternative."
                    ),
                }


            return {
                "route_available": False,
                "primary_corridor_id":
                    corridor.corridor_id,
                "primary_corridor":
                    corridor.name,
                "primary_status":
                    corridor.status,
                "alternative_corridor":
                    (
                        alternative.name
                        if alternative
                        else None
                    ),
                "alternative_status":
                    (
                        alternative.status
                        if alternative
                        else None
                    ),
                "route_decision":
                    "blocked",
                "reason": (
                    f"{corridor.name} is "
                    f"blocked and no usable "
                    f"alternative corridor "
                    f"is available."
                ),
            }


        return {
            "route_available": False,
            "primary_corridor_id":
                corridor.corridor_id,
            "primary_corridor":
                corridor.name,
            "primary_status":
                corridor.status,
            "alternative_corridor":
                None,
            "alternative_status":
                None,
            "route_decision":
                "blocked",
            "reason": (
                "Unsupported road status: "
                f"{corridor.status}"
            ),
        }
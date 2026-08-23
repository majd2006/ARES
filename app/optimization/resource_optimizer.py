class ResourceOptimizer:

    def __init__(
        self,
        distance_weight=0.35,
        sufficiency_weight=0.30,
        reserve_weight=0.20,
        capacity_weight=0.15,
    ):

        self.distance_weight = distance_weight

        self.sufficiency_weight = (
            sufficiency_weight
        )

        self.reserve_weight = (
            reserve_weight
        )

        self.capacity_weight = (
            capacity_weight
        )


    # ======================================================
    # NORMALIZATION
    # ======================================================

    def _normalize(
        self,
        value,
        minimum,
        maximum,
    ):

        if maximum == minimum:
            return 0.0

        return (
            value - minimum
        ) / (
            maximum - minimum
        )


    # ======================================================
    # SCORE CANDIDATES
    # ======================================================

    def rank_candidates(
        self,
        candidates,
        required_quantity,
    ):

        if not candidates:
            return []

        distances = [
            candidate["distance_km"]
            for candidate in candidates
        ]

        capacities = [
            candidate["available"]
            for candidate in candidates
        ]

        min_distance = min(
            distances
        )

        max_distance = max(
            distances
        )

        min_capacity = min(
            capacities
        )

        max_capacity = max(
            capacities
        )

        ranked = []

        for candidate in candidates:

            distance_score = (
                self._normalize(
                    candidate[
                        "distance_km"
                    ],
                    min_distance,
                    max_distance,
                )
            )

            available = (
                candidate[
                    "available"
                ]
            )

            # ------------------------------------------------
            # SUFFICIENCY
            # ------------------------------------------------

            if available >= required_quantity:

                sufficiency_score = 0.0

            else:

                shortage_ratio = (
                    required_quantity
                    - available
                ) / required_quantity

                sufficiency_score = (
                    min(
                        shortage_ratio,
                        1.0,
                    )
                )

            # ------------------------------------------------
            # RESERVE PRESERVATION
            # ------------------------------------------------

            allocation = min(
                available,
                required_quantity,
            )

            remaining_after_dispatch = (
                available
                - allocation
            )

            if available > 0:

                remaining_ratio = (
                    remaining_after_dispatch
                    / available
                )

            else:

                remaining_ratio = 0

            # Higher remaining reserve is better.
            reserve_score = (
                1
                - remaining_ratio
            )

            # ------------------------------------------------
            # CAPACITY SCORE
            # ------------------------------------------------

            normalized_capacity = (
                self._normalize(
                    available,
                    min_capacity,
                    max_capacity,
                )
            )

            # Higher capacity is better,
            # so invert it.
            capacity_score = (
                1
                - normalized_capacity
            )

            # ------------------------------------------------
            # FINAL SCORE
            # ------------------------------------------------

            total_score = (
                distance_score
                * self.distance_weight

                +

                sufficiency_score
                * self.sufficiency_weight

                +

                reserve_score
                * self.reserve_weight

                +

                capacity_score
                * self.capacity_weight
            )

            ranked_candidate = {
                **candidate,

                "optimization": {

                    "distance_score":
                        round(
                            distance_score,
                            3,
                        ),

                    "sufficiency_score":
                        round(
                            sufficiency_score,
                            3,
                        ),

                    "reserve_score":
                        round(
                            reserve_score,
                            3,
                        ),

                    "capacity_score":
                        round(
                            capacity_score,
                            3,
                        ),

                    "total_score":
                        round(
                            total_score,
                            3,
                        ),
                },
            }

            ranked.append(
                ranked_candidate
            )

        ranked.sort(
            key=lambda candidate:
                candidate[
                    "optimization"
                ][
                    "total_score"
                ]
        )

        return ranked
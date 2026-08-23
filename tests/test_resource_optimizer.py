from app.optimization.resource_optimizer import (
    ResourceOptimizer,
)


optimizer = ResourceOptimizer()


candidates = [

    {
        "name":
            "Relief Center Beta",

        "distance_km":
            2.35,

        "available":
            8,
    },

    {
        "name":
            "Relief Center Gamma",

        "distance_km":
            3.60,

        "available":
            14,
    },

    {
        "name":
            "Relief Center Delta",

        "distance_km":
            1.40,

        "available":
            2,
    },
]


ranked = (
    optimizer.rank_candidates(
        candidates=candidates,
        required_quantity=4,
    )
)


print(
    "ARES RESOURCE OPTIMIZATION"
)

print(
    "=========================="
)


for index, candidate in enumerate(
    ranked,
    start=1,
):

    print()

    print(
        f"Rank #{index}"
    )

    print(
        candidate["name"]
    )

    print(
        "Distance:",
        candidate[
            "distance_km"
        ],
        "km",
    )

    print(
        "Available:",
        candidate[
            "available"
        ],
    )

    print(
        "Total score:",
        candidate[
            "optimization"
        ][
            "total_score"
        ],
    )

    print(
        "Breakdown:",
        candidate[
            "optimization"
        ],
    )
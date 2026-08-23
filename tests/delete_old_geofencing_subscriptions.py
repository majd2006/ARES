from app.network.nokia_geofencing import (
    delete_geofence_subscription,
)


subscription_ids = [
    "1e4bfd03-e7c2-412c-841b-e08fa4456adf",
    "8d9963aa-28ee-42ee-aaa6-40647c803e1f",
]


print("ARES GEOFENCING CLEANUP")
print("=======================")

for subscription_id in subscription_ids:

    print()
    print(
        "Deleting:",
        subscription_id,
    )

    try:

        result = delete_geofence_subscription(
            subscription_id
        )

        print("Deleted.")
        print(result)

    except Exception as error:

        print(
            "Could not delete:",
            error,
        )
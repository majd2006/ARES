import os

from dotenv import load_dotenv
from network_as_code import NetworkAsCodeApi


load_dotenv()


NOKIA_API_KEY = os.getenv(
    "NOKIA_API_KEY"
)


def get_client():

    if not NOKIA_API_KEY:
        raise RuntimeError(
            "NOKIA_API_KEY is missing."
        )

    return NetworkAsCodeApi(
        api_key=NOKIA_API_KEY,
        rapidapi_host=(
            "network-as-code.nokia.rapidapi.com"
        ),
    )


def create_geofence_subscription(
    phone_number,
    latitude,
    longitude,
    radius_m,
    sink_url,
    event_type="area-entered",
):

    client = get_client()

    if event_type not in {
        "area-entered",
        "area-left",
    }:
        raise ValueError(
            "event_type must be "
            "'area-entered' or 'area-left'."
        )

    camara_event_type = (
        "org.camaraproject."
        "geofencing-subscriptions.v0."
        f"{event_type}"
    )

    subscription = (
        client.geofencing.create_subscription(
            protocol="HTTP",

            sink=sink_url,

            types=[
                camara_event_type
            ],

            config={
                "subscription_detail": {
                    "device": {
                        "phone_number":
                            phone_number
                    },

                    "area": {
                        "area_type":
                            "CIRCLE",

                        "center": {
                            "latitude":
                                latitude,

                            "longitude":
                                longitude,
                        },

                        "radius":
                            radius_m,
                    },
                },

                "initial_event":
                    False,

                "subscription_max_events":
                    10,
            },
        )
    )

    return subscription


def list_geofence_subscriptions():

    client = get_client()

    return (
        client.geofencing
        .list_subscriptions()
    )


def delete_geofence_subscription(
    subscription_id,
):

    client = get_client()

    return (
        client.geofencing
        .delete_subscription(
            subscription_id
        )
    )
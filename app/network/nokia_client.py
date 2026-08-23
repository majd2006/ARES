import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("NOKIA_API_KEY")

REACHABILITY_URL = (
    "https://network-as-code.p-eu.apihub.nokia.io/"
    "device-status/device-reachability-status/v1/retrieve"
)

LOCATION_URL = (
    "https://network-as-code.p-eu.apihub.nokia.io/"
    "location-retrieval/v0/retrieve"
)


def get_reachability_status(phone_number: str):
    if not API_KEY:
        raise RuntimeError(
            "NOKIA_API_KEY is missing. Add it to the .env file."
        )

    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Host": "network-as-code.nokia.rapidapi.com",
        "X-RapidAPI-Key": API_KEY,
    }

    payload = {
        "device": {
            "phoneNumber": phone_number
        }
    }

    response = requests.post(
        REACHABILITY_URL,
        headers=headers,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def get_device_location(phone_number: str, max_age: int = 60):
    if not API_KEY:
        raise RuntimeError(
            "NOKIA_API_KEY is missing. Add it to the .env file."
        )

    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Host": "network-as-code.nokia.rapidapi.com",
        "X-RapidAPI-Key": API_KEY,
    }

    payload = {
        "device": {
            "phoneNumber": phone_number
        },
        "maxAge": max_age
    }

    response = requests.post(
        LOCATION_URL,
        headers=headers,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()
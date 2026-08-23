from app.network.nokia_geofencing import (
    create_geofence_subscription,
)


print("ARES NOKIA GEOFENCING")
print("=====================")

phone_number = "+99999991000"

latitude = 47.490
longitude = 19.080

radius_m = 500

sink_url = (
    "https://rendering-anything-satin.ngrok-free.dev"
    "/api/events/geofence"
)


print()
print("Device:", phone_number)
print("Center:", latitude, longitude)
print("Radius:", radius_m, "meters")


# ==========================================================
# AREA ENTERED
# ==========================================================

print()
print("Creating AREA ENTERED subscription...")

entered_subscription = create_geofence_subscription(
    phone_number=phone_number,
    latitude=latitude,
    longitude=longitude,
    radius_m=radius_m,
    sink_url=sink_url,
    event_type="area-entered",
)

print()
print("AREA ENTERED subscription:")
print(entered_subscription)


# ==========================================================
# AREA LEFT
# ==========================================================

print()
print("Creating AREA LEFT subscription...")

left_subscription = create_geofence_subscription(
    phone_number=phone_number,
    latitude=latitude,
    longitude=longitude,
    radius_m=radius_m,
    sink_url=sink_url,
    event_type="area-left",
)

print()
print("AREA LEFT subscription:")
print(left_subscription)


print()
print("ARES geofencing subscriptions created successfully.")
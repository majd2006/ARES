from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
    disaster_zones,
)


print("ARES Demo Scenario")
print("------------------")

print("\nResponder Teams:")
for team in responder_teams:
    print(team)

print("\nHospitals:")
for hospital in hospitals:
    print(hospital)

print("\nRelief Centers:")
for center in relief_centers:
    print(center)

print("\nDisaster Zones:")
for zone in disaster_zones:
    print(zone)
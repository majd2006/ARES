from app.optimization.responder_ranker import ResponderRanker
from data.demo_scenario import responder_teams, disaster_zones


ranker = ResponderRanker()

zone = disaster_zones[0]

ranked_responders = ranker.rank_responders(
    responders=responder_teams,
    disaster_zone=zone,
)

print("ARES Responder Ranking")
print("----------------------")
print(f"Disaster Zone: {zone.name}")

for index, responder in enumerate(ranked_responders, start=1):
    print(f"\nRank #{index}")
    print(f"Team: {responder['team_id']} - {responder['name']}")
    print(f"Type: {responder['team_type']}")
    print(f"Members: {responder['members']}")
    print(f"Reachable: {responder['reachable']}")
    print(
        f"Distance: {responder['distance_to_disaster_km']} km"
    )
    
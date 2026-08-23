from app.agents.operational_strategy_agent import (
    OperationalStrategyAgent,
)
from app.agents.response_planning_agent import (
    ResponsePlanningAgent,
)
from app.optimization.responder_ranker import (
    ResponderRanker,
)
from app.agents.responder_evaluator import (
    ResponderEvaluator,
)
from data.demo_scenario import (
    responder_teams,
    hospitals,
    relief_centers,
    disaster_zones,
)


zone = disaster_zones[0]

evaluator = ResponderEvaluator()
ranker = ResponderRanker()
planner = ResponsePlanningAgent()
strategy_agent = OperationalStrategyAgent()


evaluated_responders = []

for responder in responder_teams:
    result = evaluator.evaluate_responder(
        responder=responder,
        disaster_latitude=zone.latitude,
        disaster_longitude=zone.longitude,
    )

    result["team_id"] = responder.team_id
    result["name"] = responder.name
    result["team_type"] = responder.team_type
    result["members"] = responder.members

    evaluated_responders.append(result)


ranked_responders = ranker.rank_responders(
    responders=responder_teams,
    disaster_zone=zone,
)


plan = planner.generate_plan(
    disaster_zone=zone,
    responders=ranked_responders,
    hospitals=hospitals,
    relief_centers=relief_centers,
)


strategy = strategy_agent.generate_strategy(
    disaster_zone=zone,
    response_plan=plan,
    all_responders=evaluated_responders,
)


print("ARES OPERATIONAL STRATEGY")
print("=========================")

for action in strategy["actions"]:
    print(
        f"\n[{action['priority']}] "
        f"{action['category']}"
    )

    print(
        action["title"]
    )

    print(
        action["description"]
    )
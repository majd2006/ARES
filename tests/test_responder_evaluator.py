from app.agents.responder_evaluator import ResponderEvaluator


evaluator = ResponderEvaluator()

# For this first test, use a disaster location close to
# Nokia's simulated responder location.
disaster_latitude = 47.4900
disaster_longitude = 19.0800

result = evaluator.evaluate_responder(
    phone_number="+99999991000",
    disaster_latitude=disaster_latitude,
    disaster_longitude=disaster_longitude,
)

print("ARES Responder Evaluation")
print("-------------------------")

for key, value in result.items():
    print(f"{key}: {value}")

if result["eligible_for_deployment"]:
    print("\nARES Decision: Responder is eligible for deployment.")
else:
    print("\nARES Decision: Responder is not currently eligible.")
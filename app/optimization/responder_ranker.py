from app.agents.responder_evaluator import ResponderEvaluator


class ResponderRanker:
    def __init__(self):
        self.evaluator = ResponderEvaluator()

    def rank_responders(self, responders, disaster_zone):
        evaluated = []

        for responder in responders:
            if not responder.available:
                continue

            result = self.evaluator.evaluate_responder(
                responder=responder,
                disaster_latitude=disaster_zone.latitude,
                disaster_longitude=disaster_zone.longitude,
            )
            

            result["team_id"] = responder.team_id
            result["name"] = responder.name
            result["team_type"] = responder.team_type
            result["members"] = responder.members

            evaluated.append(result)

        eligible = [
            responder
            for responder in evaluated
            if responder["eligible_for_deployment"]
        ]

        eligible.sort(
            key=lambda responder: responder["distance_to_disaster_km"]
        )

        return eligible
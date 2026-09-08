"""Isolated runtime regressions; telecom fixtures are test-only, not live evidence."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import app.main as dashboard
from app.orchestration.ares_orchestrator import ARESOrchestrator
from app.orchestration.decision_replanner import DecisionReplanner
from app.orchestration.command_approval import CommandApprovalManager
from tests.test_orchestrator_resilience import build_incident
from data.demo_scenario import responder_teams, hospitals, relief_centers


class RuntimeResourcePressureTests(unittest.TestCase):
    def setUp(self):
        fixture = patch('app.agents.network_agent.get_reachability_status',
                        return_value={'reachable': True, 'connectivity': ['DATA']})
        fixture.start()
        self.addCleanup(fixture.stop)
        location = patch('app.agents.network_agent.get_device_location',
                         side_effect=AssertionError('Location deliberately skipped'))
        self.location = location.start()
        self.addCleanup(location.stop)

    def test_pressure_strategy_and_dataset(self):
        orchestrator = ARESOrchestrator()
        before_data = deepcopy(relief_centers)
        kwargs = dict(incident=build_incident(), responders=responder_teams,
                      hospitals=hospitals, relief_centers=relief_centers,
                      operational_location_mode='registered_scenario')
        before = orchestrator.run_incident(**kwargs)
        after = orchestrator.run_incident(**kwargs, resource_pressure=True)
        for key in ('ambulances', 'medical_teams'):
            self.assertGreater(before['response_plan']['reserve_resources'][key], 0)
            self.assertEqual(after['response_plan']['reserve_resources'][key], 0)
        reserve_action = next(a for a in after['operational_strategy']['actions']
                              if a['category'] == 'Operational Reserve')
        self.assertIn('0 medical teams, 0 ambulances', reserve_action['description'])
        self.assertEqual(before_data, relief_centers)
        self.assertTrue(DecisionReplanner().compare(before, after,
                        trigger={'type': 'resource_pressure'})['requires_replanning'])
        self.location.assert_not_called()

    def test_only_outside_excludes_geographically(self):
        orchestrator = ARESOrchestrator()
        team = responder_teams[0]
        for status in ('inside', 'outside', 'initializing', 'unknown',
                       'subscription_ended', None):
            with self.subTest(status=status):
                result = orchestrator.evaluate_responders(
                    [team], build_incident(), operational_location_mode='registered_scenario',
                    geofence_status_by_team={team.team_id: status})[0]
                self.assertTrue(result['reachable'])
                self.assertEqual(result['geofence_eligible'], status != 'outside')
                self.assertEqual(result['eligible_for_deployment'], status != 'outside')

    def test_dashboard_and_sequential_events(self):
        for name in ('scenario_state', 'simulation_state', 'geofence_state',
                     'replanning_state', 'reassessment_state'):
            original = deepcopy(getattr(dashboard, name))
            self.addCleanup(setattr, dashboard, name, original)
        self.addCleanup(setattr, dashboard, 'active_incident', dashboard.active_incident)
        original_approval = deepcopy(dashboard.command_approval_manager.state)
        self.addCleanup(setattr, dashboard.command_approval_manager, 'state', original_approval)
        self.addCleanup(dashboard.app.config.update, TESTING=dashboard.app.config['TESTING'])
        client = dashboard.app.test_client()
        dashboard.app.config['TESTING'] = True
        for scenario in ('standard', 'beirut'):
            with self.subTest(scenario=scenario):
                self.assertEqual(client.post('/api/demo/scenario',
                    json={'scenario_id': scenario}).status_code, 200)
                self.assertEqual(client.get('/').status_code, 200)
                data_before = deepcopy(dashboard.get_active_scenario()['relief_centers'])
                manager = dashboard.command_approval_manager
                previous_version = manager.state['decision_version']
                manager.approve('Regression test commander', decision_version=previous_version)
                generated_decisions = []
                run_incident = dashboard.ares_orchestrator.run_incident

                def capture_decision(*args, **kwargs):
                    decision = run_incident(*args, **kwargs)
                    generated_decisions.append(decision)
                    return decision

                with patch.object(dashboard.ares_orchestrator, 'run_incident',
                                  side_effect=capture_decision):
                    response = client.post('/api/simulations/resource-pressure')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(generated_decisions), 2)
                self.assertIs(dashboard.replanning_state['current_decision'], generated_decisions[1])
                self.assertIs(dashboard.replanning_state['previous_decision'], generated_decisions[0])
                self.assertEqual(generated_decisions[1]['response_plan']['reserve_resources']['ambulances'], 0)
                approval = response.json['command_approval']
                self.assertEqual(approval['decision_version'], previous_version + 1)
                self.assertEqual(approval['status'], 'pending_approval')
                self.assertIsNone(approval['approved_version'])
                self.assertFalse(approval['authorized'])
                self.assertIsInstance(approval['notes'], str)
                self.assertIn('resource pressure', approval['notes'])
                self.assertEqual(approval['history'][0]['notes'], approval['notes'])
                self.assertEqual(approval['history'][0]['decision_version'], previous_version + 1)
                self.assertTrue(dashboard.replanning_state['last_result']['requires_replanning'])
                self.assertFalse(dashboard.replanning_state['previous_decision']
                                 ['response_plan']['reserve_resources']['ambulances'] == 0)
                if scenario == 'beirut':
                    self.assertEqual(client.post('/api/simulations/road-obstruction',
                                     json={'corridor_id': 'BR-05'}).status_code, 200)
                team = dashboard.get_active_scenario()['responders'][1]
                self.assertEqual(client.post('/api/events/geofence', json={
                    'type': 'org.camaraproject.geofencing-subscriptions.v0.area-left',
                    'source': 'isolated_test_simulated_callback',
                    'data': {'device': {'phoneNumber': team.phone_number}}}).status_code, 200)
                first = dashboard.get_active_scenario()['responders'][0]
                self.assertEqual(client.post('/api/simulations/network-outage',
                                 json={'team_id': first.team_id}).status_code, 200)
                decision = dashboard.replanning_state['current_decision']
                self.assertEqual(decision['response_plan']['reserve_resources']['ambulances'], 0)
                excluded = next(r for r in decision['responders'] if r['team_id'] == team.team_id)
                self.assertTrue(excluded['reachable'])
                self.assertFalse(excluded['eligible_for_deployment'])
                if scenario == 'beirut':
                    self.assertTrue(any(r['runtime_route_override'] for r in decision['responders']))
                    for responder in decision['responders']:
                        if not responder['route_available']:
                            self.assertFalse(responder['eligible_for_deployment'])
                state = dashboard.build_dashboard_state()
                for resource in ('medical_teams', 'ambulances', 'volunteers'):
                    self.assertLessEqual(state['field_medical_post'][resource + '_required'],
                                         state['response_plan']['recommended_resources'][resource])
                self.assertEqual(data_before, dashboard.get_active_scenario()['relief_centers'])
                self.assertEqual(dashboard.command_approval_manager.state['status'], 'pending_approval')
                self.assertEqual(client.get('/').status_code, 200)
                self.assertEqual(client.post('/api/simulations/resource-pressure').json['status'],
                                 'already_active')

    def test_field_post_cannot_exceed_small_mobilization(self):
        from app.agents.field_medical_post_agent import FieldMedicalPostAgent
        from types import SimpleNamespace
        plan = {'recommended_resources': {'medical_teams': 0, 'ambulances': 1,
                                          'volunteers': 3},
                'hospital_allocations': [], 'unallocated_critical_patients': 100}
        result = FieldMedicalPostAgent().evaluate(
            SimpleNamespace(estimated_critical=100, estimated_casualties=1000),
            plan, hospitals, relief_centers)
        self.assertTrue(result['required'])
        for resource, count in plan['recommended_resources'].items():
            self.assertLessEqual(result[resource + '_required'], count)

    def test_invalid_registration_reason_does_not_change_approval(self):
        manager = CommandApprovalManager()
        manager.approve('Regression test commander')
        before = manager.get_state()
        with self.assertRaisesRegex(ValueError, 'reason must be a string or None'):
            manager.register_new_decision({'response_plan': {}})
        self.assertEqual(manager.get_state(), before)
        manager.register_new_decision(reason=None)
        self.assertEqual(manager.state['status'], 'pending_approval')
        self.assertIsNone(manager.state['notes'])
        self.assertIsNone(manager.state['history'][0]['notes'])


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import static_routes
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestStaticRoutesModule(TestModuleBase):

    module = static_routes

    def setUp(self):
        super(TestStaticRoutesModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.static_routes.StaticRoutesFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestStaticRoutesModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("static_routes_config.cfg")
        self.get_device_data.side_effect = load_from_file

    def test_static_routes_create_merged(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '10.0.0.0',
                    'destination_netmask': 8,
                    'gateway_address': '10.0.0.1',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'static_routes/',
                'data': {
                    'static_route': {
                        'destination_address': '10.0.0.0',
                        'destination_netmask': 8,
                        'gateway_address': '10.0.0.1',
                        'metric': 200,
                    }
                },
                'method': 'POST'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_static_routes_create_merged_idempotent(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'destination_netmask': 24,
                    'gateway_address': '10.0.0.1',
                    'interface': 'eth0',
                    'metric': 100,
                }
            ],
            'state': 'merged',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_static_routes_update_merged(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'static_routes/static_routes-1',
                'data': {
                    'static_route': {
                        'destination_address': '192.168.10.0',
                        'destination_netmask': 24,
                        'gateway_address': '10.0.0.1',
                        'interface': 'eth0',
                        'metric': 200,
                    }
                },
                'method': 'PUT'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_static_routes_update_replaced(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'destination_netmask': 24,
                    'gateway_address': '10.0.0.2',
                    'metric': 100,
                }
            ],
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'static_routes/static_routes-1',
                'data': {
                    'static_route': {
                        'destination_address': '192.168.10.0',
                        'destination_netmask': 24,
                        'gateway_address': '10.0.0.2',
                        'metric': 100,
                    }
                },
                'method': 'PUT'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_static_routes_update_overridden(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '10.0.0.0',
                    'destination_netmask': 8,
                    'gateway_address': '10.0.0.1',
                    'metric': 100,
                }
            ],
            'state': 'overridden',
        })

        # No existing routes match 10.0.0.0, so bulk PUT replaces all
        commands = [
            {
                'path': 'static_routes/',
                'data': {
                    'static_routes': [
                        {
                            'destination_address': '10.0.0.0',
                            'destination_netmask': 8,
                            'gateway_address': '10.0.0.1',
                            'metric': 100,
                        }
                    ]
                },
                'method': 'PUT'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_static_routes_overridden_idempotent_when_none_exist_and_none_wanted(self):
        """Overridden with no routes wanted and none on the device must be no-op"""
        self.load_fixtures = lambda commands=None, filename=None: (
            self.get_device_data.configure_mock(side_effect=None, return_value=[])
        )
        set_module_args({
            'config': [],
            'state': 'overridden',
        })
        self.execute_module(changed=False, commands=[])

    def test_static_routes_deleted(self):
        set_module_args({
            'config': [
                {'destination_address': '192.168.10.0'}
            ],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'static_routes/static_routes-1',
                'data': None,
                'method': 'DELETE'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_static_routes_gathered(self):
        set_module_args({
            'state': 'gathered',
        })

        result = self.execute_module(changed=False)
        self.assertIn('gathered', result)
        routes = result['gathered']
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]['destination_address'], '192.168.10.0')
        self.assertEqual(routes[1]['destination_address'], '172.16.0.0')

    def test_static_routes_rendered(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '10.0.0.0',
                    'destination_netmask': 8,
                    'gateway_address': '10.0.0.1',
                }
            ],
            'state': 'rendered',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_static_routes_check_mode(self):
        set_module_args({
            '_ansible_check_mode': True,
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

    def test_static_routes_diff_merged_create(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'destination_address': '10.0.0.0',
                    'destination_netmask': 8,
                    'gateway_address': '10.0.0.1',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(len(after), 1)
        self.assertEqual(before[0], {})
        self.assertEqual(after[0]['destination_address'], '10.0.0.0')

    def test_static_routes_diff_merged_update(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(len(after), 1)
        self.assertEqual(before[0]['destination_address'], '192.168.10.0')
        self.assertEqual(before[0]['metric'], 100)
        self.assertEqual(after[0]['metric'], 200)

    def test_static_routes_diff_deleted(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {'destination_address': '192.168.10.0'}
            ],
            'state': 'deleted',
        })

        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(before[0]['destination_address'], '192.168.10.0')
        self.assertEqual(after[0], {})

    def test_static_routes_no_diff_when_not_requested(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_static_routes_no_diff_when_idempotent(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'destination_netmask': 24,
                    'gateway_address': '10.0.0.1',
                    'interface': 'eth0',
                    'metric': 100,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_static_routes_check_mode_with_diff_merged(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'metric': 200,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(len(after), 1)
        self.assertEqual(before[0]['destination_address'], '192.168.10.0')
        self.assertEqual(before[0]['metric'], 100)
        self.assertEqual(after[0]['metric'], 200)

    def test_static_routes_check_mode_with_diff_deleted(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {'destination_address': '172.16.0.0'}
            ],
            'state': 'deleted',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()

        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(before[0]['destination_address'], '172.16.0.0')
        self.assertEqual(after[0], {})

    def test_static_routes_replaced_idempotent(self):
        set_module_args({
            'config': [
                {
                    'destination_address': '192.168.10.0',
                    'destination_netmask': 24,
                    'gateway_address': '10.0.0.1',
                    'interface': 'eth0',
                    'metric': 100,
                }
            ],
            'state': 'replaced',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

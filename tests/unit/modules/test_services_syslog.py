# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import services_syslog
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestServicesSyslogModule(TestModuleBase):

    module = services_syslog

    def setUp(self):
        super(TestServicesSyslogModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.services_syslog.ServicesSyslogFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestServicesSyslogModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("services_syslog.cfg")

    # --- merged ---
    def test_merged_add(self):
        set_module_args({
            'config': [{
                'address': 'syslog.example.com',
                'port': 514,
                'protocol': 'UDP',
                'min_severity': 'warning',
            }],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/syslog',
                'data': {'syslogServer': {
                    'address': 'syslog.example.com',
                    'port': 514,
                    'protocol': 'UDP',
                    'min_severity': 'warning',
                }},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_idempotent(self):
        set_module_args({
            'config': [{
                'address': '192.168.33.200',
                'port': 705,
                'protocol': 'UDP',
                'description': 'Remote logging server',
                'port_logging_enabled': False,
                'min_severity': 'warning',
            }],
            'state': 'merged',
        })

        self.execute_module(changed=False, commands=[])

    def test_merged_updates_existing(self):
        """A partial update to an existing server merges onto its current
        fields and pushes a PUT with the complete record"""
        set_module_args({
            'config': [{
                'address': '192.168.33.200',
                'port': 705,
                'protocol': 'UDP',
                'min_severity': 'critical',
            }],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/syslog/services_syslog_servers-1',
                'data': {'syslogServer': {
                    'address': '192.168.33.200',
                    'port': 705,
                    'protocol': 'UDP',
                    'description': 'Remote logging server',
                    'port_logging_enabled': False,
                    'min_severity': 'critical',
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- overridden ---
    def test_overridden_converges(self):
        """Keep the matching server, delete the one not listed"""
        set_module_args({
            'config': [{
                'address': '192.168.33.200',
                'port': 705,
                'protocol': 'UDP',
            }],
            'state': 'overridden',
        })

        commands = [
            {
                'path': 'services/syslog/services_syslog_servers-2',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- deleted ---
    def test_deleted_existing(self):
        set_module_args({
            'config': [{
                'address': '192.168.33.200',
                'port': 705,
                'protocol': 'UDP',
            }],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'services/syslog/services_syslog_servers-1',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_deleted_idempotent(self):
        set_module_args({
            'config': [{
                'address': 'nonexistent.example.com',
                'port': 1,
                'protocol': 'UDP',
            }],
            'state': 'deleted',
        })

        self.execute_module(changed=False, commands=[])

    # --- gathered ---
    def test_gathered(self):
        set_module_args({'state': 'gathered'})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(len(gathered), 2)
        self.assertEqual(gathered[0]['id'], 'services_syslog_servers-1')
        self.assertEqual(gathered[0]['address'], '192.168.33.200')

    # --- rendered ---
    def test_rendered(self):
        set_module_args({
            'config': [{
                'address': 'syslog.example.com',
                'port': 514,
                'protocol': 'UDP',
            }],
            'state': 'rendered',
        })

        result = self.execute_module(changed=False)
        self.assertEqual(
            result['rendered'],
            [
                {
                    'path': 'services/syslog',
                    'data': {'syslogServer': {
                        'address': 'syslog.example.com',
                        'port': 514,
                        'protocol': 'UDP',
                    }},
                    'method': 'POST',
                }
            ],
        )

    # --- diff mode ---

    def test_diff_mode_when_changed(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [{
                'address': 'syslog.example.com',
                'port': 514,
                'protocol': 'UDP',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertIsInstance(before, list)
        self.assertIsInstance(after, list)

    def test_no_diff_when_not_requested(self):
        set_module_args({
            'config': [{
                'address': 'syslog.example.com',
                'port': 514,
                'protocol': 'UDP',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_no_diff_when_idempotent(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [{
                'address': '192.168.33.200',
                'port': 705,
                'protocol': 'UDP',
                'description': 'Remote logging server',
                'port_logging_enabled': False,
                'min_severity': 'warning',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_check_mode_with_diff_shows_new_server(self):
        """Check mode combined with diff mode must show the new server, not
        just re-echo the unchanged device facts as 'after'."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [{
                'address': 'syslog.example.com',
                'port': 514,
                'protocol': 'UDP',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertFalse(any(s['address'] == 'syslog.example.com' for s in before))
        self.assertTrue(any(s['address'] == 'syslog.example.com' for s in after))

    def test_check_mode_with_diff_shows_updated_server(self):
        """Check mode combined with diff mode must show the updated field,
        not just re-echo the unchanged device facts as 'after'."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [{
                'address': '192.168.33.200',
                'port': 705,
                'protocol': 'UDP',
                'min_severity': 'critical',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        before_server = next(s for s in before if s['address'] == '192.168.33.200')
        after_server = next(s for s in after if s['address'] == '192.168.33.200')
        self.assertEqual(before_server['min_severity'], 'warning')
        self.assertEqual(after_server['min_severity'], 'critical')

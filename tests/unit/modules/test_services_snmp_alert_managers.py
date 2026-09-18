# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import services_snmp_alert_managers
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestServicesSnmpAlertManagersModule(TestModuleBase):

    module = services_snmp_alert_managers

    def setUp(self):
        super(TestServicesSnmpAlertManagersModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.services_snmp_alert_managers.ServicesSnmpAlertManagersFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestServicesSnmpAlertManagersModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("services_snmp_alert_managers.cfg")

    # --- merged ---
    def test_merged_add(self):
        set_module_args({
            'config': [{
                'name': 'Third NMS',
                'protocol': 'UDP',
                'address': 'third.example.com',
                'port': 162,
                'version': 'v2c',
                'msg_type': 'TRAP',
                'community': 'public',
            }],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/snmp_alert_managers',
                'data': {'snmp_alert_manager': {
                    'name': 'Third NMS',
                    'protocol': 'UDP',
                    'address': 'third.example.com',
                    'port': 162,
                    'version': 'v2c',
                    'msg_type': 'TRAP',
                    'community': 'public',
                }},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_idempotent(self):
        set_module_args({
            'config': [{
                'name': 'Backup NMS',
                'protocol': 'UDP',
                'address': 'backup.example.com',
                'port': 162,
                'version': 'v2c',
                'msg_type': 'TRAP',
                'community': 'public',
            }],
            'state': 'merged',
        })

        self.execute_module(changed=False, commands=[])

    def test_merged_updates_existing(self):
        """A partial update to an existing manager merges onto its current
        fields and pushes a PUT with the complete record"""
        set_module_args({
            'config': [{
                'address': 'backup.example.com',
                'port': 162,
                'protocol': 'UDP',
                'community': 'newsecret',
            }],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/snmp_alert_managers/snmp_manager_2',
                'data': {'snmp_alert_manager': {
                    'name': 'Backup NMS',
                    'protocol': 'UDP',
                    'address': 'backup.example.com',
                    'port': 162,
                    'msg_type': 'TRAP',
                    'version': 'v2c',
                    'community': 'newsecret',
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- overridden ---
    def test_overridden_converges(self):
        set_module_args({
            'config': [{'address': 'backup.example.com', 'port': 162, 'protocol': 'UDP'}],
            'state': 'overridden',
        })

        commands = [
            {
                'path': 'services/snmp_alert_managers/snmp_manager_1',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- deleted ---
    def test_deleted_existing(self):
        set_module_args({
            'config': [{'address': 'snmp.example.com', 'port': 167, 'protocol': 'UDP'}],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'services/snmp_alert_managers/snmp_manager_1',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_deleted_idempotent(self):
        set_module_args({
            'config': [{'address': 'nonexistent.example.com', 'port': 162, 'protocol': 'UDP'}],
            'state': 'deleted',
        })

        self.execute_module(changed=False, commands=[])

    # --- gathered ---
    def test_gathered(self):
        set_module_args({'state': 'gathered'})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(len(gathered), 2)
        self.assertEqual(gathered[0]['name'], 'Primary NMS')

    # --- rendered ---
    def test_rendered(self):
        set_module_args({
            'config': [{'name': 'Third NMS', 'address': 'third.example.com'}],
            'state': 'rendered',
        })

        result = self.execute_module(changed=False)
        self.assertEqual(
            result['rendered'],
            [
                {
                    'path': 'services/snmp_alert_managers',
                    'data': {'snmp_alert_manager': {
                        'name': 'Third NMS',
                        'address': 'third.example.com',
                    }},
                    'method': 'POST',
                }
            ],
        )

    # --- diff mode ---

    def test_diff_mode_when_changed(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [{'name': 'Third NMS', 'address': 'third.example.com'}],
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
            'config': [{'name': 'Third NMS', 'address': 'third.example.com'}],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_no_diff_when_idempotent(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [{
                'name': 'Backup NMS',
                'protocol': 'UDP',
                'address': 'backup.example.com',
                'port': 162,
                'version': 'v2c',
                'msg_type': 'TRAP',
                'community': 'public',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_check_mode_with_diff_shows_new_manager(self):
        """Check mode combined with diff mode must show the new manager,
        not just re-echo the unchanged device facts as 'after'."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [{
                'name': 'Third NMS',
                'protocol': 'UDP',
                'address': 'third.example.com',
                'port': 162,
                'version': 'v2c',
                'msg_type': 'TRAP',
                'community': 'public',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertFalse(any(m['name'] == 'Third NMS' for m in before))
        self.assertTrue(any(m['name'] == 'Third NMS' for m in after))

    def test_check_mode_with_diff_shows_updated_manager(self):
        """Check mode combined with diff mode must show the updated field,
        not just re-echo the unchanged device facts as 'after'."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [{
                'address': 'backup.example.com',
                'port': 162,
                'protocol': 'UDP',
                'community': 'newsecret',
            }],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        before_manager = next(m for m in before if m['name'] == 'Backup NMS')
        after_manager = next(m for m in after if m['name'] == 'Backup NMS')
        self.assertEqual(before_manager['community'], 'public')
        self.assertEqual(after_manager['community'], 'newsecret')

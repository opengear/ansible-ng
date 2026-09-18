# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import system_authorized_keys
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestSystemAuthorizedKeysModule(TestModuleBase):

    module = system_authorized_keys

    def setUp(self):
        super(TestSystemAuthorizedKeysModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.system_authorized_keys.SystemAuthorizedKeysFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestSystemAuthorizedKeysModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("system_authorized_keys_config.cfg")

    ROOT_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c root@laptop"
    ADMIN_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp admin@workstation"
    NEW_KEY = "ssh-rsa AAAAB3NzaC1yc2NEWKEY root@newhost"

    # --- merged ---
    def test_merged_add_key(self):
        set_module_args({
            'config': [{'username': 'root', 'key': self.NEW_KEY}],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/system_authorized_keys',
                'data': {'system_authorized_key': {'username': 'root', 'key': self.NEW_KEY}},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_idempotent(self):
        set_module_args({
            'config': [{'username': 'root', 'key': self.ROOT_KEY}],
            'state': 'merged',
        })

        self.execute_module(changed=False, commands=[])

    def test_merged_passes_multi_field_identifier(self):
        set_module_args({
            'config': [{'username': 'root', 'key': self.NEW_KEY, 'multi_field_identifier': 'mfi-9'}],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'system/system_authorized_keys',
                'data': {'system_authorized_key': {'username': 'root', 'key': self.NEW_KEY, 'multi_field_identifier': 'mfi-9'}},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- deleted ---
    def test_deleted_existing(self):
        set_module_args({
            'config': [{'username': 'admin', 'key': self.ADMIN_KEY}],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'system/system_authorized_keys/system_authorized_keys-2',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_deleted_idempotent(self):
        set_module_args({
            'config': [{'username': 'root', 'key': self.NEW_KEY}],
            'state': 'deleted',
        })

        self.execute_module(changed=False, commands=[])

    # --- replaced ---
    def test_replaced_converges(self):
        """Keep root's key, drop admin's, add a new one for root"""
        set_module_args({
            'config': [
                {'username': 'root', 'key': self.ROOT_KEY},
                {'username': 'root', 'key': self.NEW_KEY},
            ],
            'state': 'replaced',
        })

        result = self.execute_module(changed=True)
        # admin key deleted, new root key added, existing root key untouched
        self.assertIn(
            {
                'path': 'system/system_authorized_keys/system_authorized_keys-2',
                'data': None,
                'method': 'DELETE',
            },
            result['commands'],
        )
        self.assertIn(
            {
                'path': 'system/system_authorized_keys',
                'data': {'system_authorized_key': {'username': 'root', 'key': self.NEW_KEY}},
                'method': 'POST',
            },
            result['commands'],
        )
        self.assertEqual(len(result['commands']), 2)

    # --- gathered ---
    def test_gathered(self):
        set_module_args({'state': 'gathered'})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(len(gathered), 2)
        self.assertEqual(gathered[0]['username'], 'root')
        self.assertEqual(gathered[0]['id'], 'system_authorized_keys-1')
        # key_fingerprint is informational and must not be returned
        self.assertNotIn('key_fingerprint', gathered[0])

    # --- diff mode ---

    def test_diff_mode_when_changed(self):
        """diff key is present when _ansible_diff is set and a change is made"""
        set_module_args({
            '_ansible_diff': True,
            'config': [{'username': 'root', 'key': self.NEW_KEY}],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertIsInstance(before, list)
        self.assertIsInstance(after, list)

    def test_no_diff_when_not_requested(self):
        """diff key is absent when _ansible_diff is not set"""
        set_module_args({
            'config': [{'username': 'root', 'key': self.NEW_KEY}],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_no_diff_when_idempotent(self):
        """diff key is absent when nothing changed"""
        set_module_args({
            '_ansible_diff': True,
            'config': [{'username': 'root', 'key': self.ROOT_KEY}],
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_check_mode_with_diff_shows_new_key(self):
        """Check mode combined with diff mode must show the new key, not
        just re-echo the unchanged device facts as 'after'."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [{'username': 'root', 'key': self.NEW_KEY}],
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertFalse(any(k['key'] == self.NEW_KEY for k in before))
        self.assertTrue(any(k['key'] == self.NEW_KEY for k in after))

    def test_check_mode_with_diff_shows_deletion(self):
        """Check mode combined with diff mode must show the key as removed,
        not just re-echo the unchanged device facts as 'after'."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [{'username': 'admin', 'key': self.ADMIN_KEY}],
            'state': 'deleted',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertTrue(any(k['key'] == self.ADMIN_KEY for k in before))
        self.assertFalse(any(k['key'] == self.ADMIN_KEY for k in after))

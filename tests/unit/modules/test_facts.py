# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import facts
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase


class TestFactsModule(TestModuleBase):

    module = facts

    def setUp(self):
        super(TestFactsModule, self).setUp()
        self.maxDiff = None

        # Mocks with at least one valid item per module are required to test the facts dispatching
        def _setup_users_mocks(self):
            mock = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.users.UsersFacts.get_device_data"
            )
            mock.start().return_value = [
                {'username': 'user1', 'id': 'users-1', 'enabled': True}
            ]
            return mock

        def _setup_groups_mocks(self):
            mock = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.groups.GroupsFacts.get_device_data"
            )
            mock.start().return_value = [
                {'groupname': 'admin', 'id': 'groups-1', 'enabled': True}
            ]
            return mock

        def _setup_firmware_upgrade_mocks(self):
            mock_version = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.firmware_upgrade.FirmwareUpgradeFacts.get_version"
            )
            mock_version.start().return_value = {
                'firmware_version': '25.04.0',
                'rest_api_version': 'v2',
            }

            mock_status = patch(
                "ansible_collections.opengear.ng.plugins.module_utils."
                "facts.firmware_upgrade.FirmwareUpgradeFacts.get_upgrade_status"
            )
            mock_status.start().return_value = {'state': 'pending'}

            return mock_version, mock_status

        self.mock_users = _setup_users_mocks(self)
        self.mock_groups = _setup_groups_mocks(self)
        self.mock_fw_version, self.mock_fw_status = _setup_firmware_upgrade_mocks(self)

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestFactsModule, self).tearDown()
        self.mock_users.stop()
        self.mock_groups.stop()
        self.mock_fw_version.stop()
        self.mock_fw_status.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        pass

    def test_facts_gather_users(self):
        """Facts module dispatches correctly to users facts class"""
        set_module_args({'gather_network_resources': ['users']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('ansible_network_resources', result['ansible_facts'])
        self.assertIn('users', result['ansible_facts']['ansible_network_resources'])

    def test_facts_gather_groups(self):
        """Facts module dispatches correctly to groups facts class"""
        set_module_args({'gather_network_resources': ['groups']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('groups', result['ansible_facts']['ansible_network_resources'])

    def test_facts_gather_firmware_upgrade(self):
        """Facts module dispatches correctly to firmware_upgrade facts class"""
        set_module_args({'gather_network_resources': ['firmware_upgrade']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('firmware_upgrade', result['ansible_facts']['ansible_network_resources'])

    def test_facts_gather_multiple(self):
        """Facts module can gather multiple resources in a single call"""
        set_module_args({'gather_network_resources': ['users', 'groups']})
        result = self.execute_module(changed=False)

        resources = result['ansible_facts']['ansible_network_resources']
        self.assertIn('users', resources)
        self.assertIn('groups', resources)

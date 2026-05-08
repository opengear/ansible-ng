from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.om.tests.unit.compat.mock import patch
from ansible_collections.opengear.om.plugins.modules import om_facts
from ansible_collections.opengear.om.tests.unit.modules.utils import set_module_args
from .om_module import TestOmModule, load_fixture


class TestOmFactsModule(TestOmModule):

    module = om_facts

    def setUp(self):
        super(TestOmFactsModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "facts.users.users.UsersFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestOmFactsModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        # Allow each test to configure its own fixtures
        pass

    def test_om_facts_gather_users(self):
        self.get_device_data.side_effect = lambda *args, **kwargs: load_fixture(
            "om_users_config.cfg"
        )

        set_module_args({
            'gather_network_resources': ['users'],
        })

        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('ansible_network_resources', result['ansible_facts'])
        self.assertIn('users', result['ansible_facts']['ansible_network_resources'])

        users = result['ansible_facts']['ansible_network_resources']['users']
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['username'], 'user1')
        self.assertEqual(users[1]['username'], 'user2')

    def test_om_facts_gather_users_empty(self):
        # Don't load any fixtures
        set_module_args({
            'gather_network_resources': ['users'],
        })

        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        users = result['ansible_facts']['ansible_network_resources'].get('users')
        self.assertFalse(users)

    def test_om_facts_gather_groups(self):
        self.get_device_data.side_effect = lambda *args, **kwargs: load_fixture(
            "om_groups_config.cfg"
        )

        set_module_args({
            'gather_network_resources': ['groups'],
        })

        self.mock_get_groups_data = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "facts.groups.groups.GroupsFacts.get_device_data"
        )

        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('groups', result['ansible_facts']['ansible_network_resources'])

        groups = result['ansible_facts']['ansible_network_resources']['groups']
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]['groupname'], 'admin')
        self.assertEqual(groups[1]['groupname'], 'netgrp')

        self.mock_get_groups_data.stop()

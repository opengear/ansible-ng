from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.om.tests.unit.compat.mock import patch
from ansible_collections.opengear.om.plugins.modules import om_facts
from ansible_collections.opengear.om.tests.unit.modules.utils import set_module_args
from .om_module import TestOmModule


class TestOmFactsModule(TestOmModule):

    module = om_facts

    def setUp(self):
        super(TestOmFactsModule, self).setUp()
        self.maxDiff = None

        # Mocks with at least one valid item per module are required to test the facts dispatching
        def _setup_users_mocks(self):
            mock = patch(
                "ansible_collections.opengear.om.plugins.module_utils.network.om."
                "facts.users.users.UsersFacts.get_device_data"
            )
            mock.start().return_value = [
                {'username': 'user1', 'id': 'users-1', 'enabled': True}
            ]
            return mock

        def _setup_groups_mocks(self):
            mock = patch(
                "ansible_collections.opengear.om.plugins.module_utils.network.om."
                "facts.groups.groups.GroupsFacts.get_device_data"
            )
            mock.start().return_value = [
                {'groupname': 'admin', 'id': 'groups-1', 'enabled': True}
            ]
            return mock

        self.mock_users = _setup_users_mocks(self)
        self.mock_groups = _setup_groups_mocks(self)

        self.mock_connection = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestOmFactsModule, self).tearDown()
        self.mock_users.stop()
        self.mock_groups.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        pass

    def test_om_facts_gather_users(self):
        """Facts module dispatches correctly to users facts class"""
        set_module_args({'gather_network_resources': ['users']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('ansible_network_resources', result['ansible_facts'])
        self.assertIn('users', result['ansible_facts']['ansible_network_resources'])

    def test_om_facts_gather_groups(self):
        """Facts module dispatches correctly to groups facts class"""
        set_module_args({'gather_network_resources': ['groups']})
        result = self.execute_module(changed=False)

        self.assertIn('ansible_facts', result)
        self.assertIn('groups', result['ansible_facts']['ansible_network_resources'])

    def test_om_facts_gather_multiple(self):
        """Facts module can gather multiple resources in a single call"""
        set_module_args({'gather_network_resources': ['users', 'groups']})
        result = self.execute_module(changed=False)

        resources = result['ansible_facts']['ansible_network_resources']
        self.assertIn('users', resources)
        self.assertIn('groups', resources)

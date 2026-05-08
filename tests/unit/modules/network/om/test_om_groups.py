from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.om.tests.unit.compat.mock import patch
from ansible_collections.opengear.om.plugins.modules import om_groups
from ansible_collections.opengear.om.tests.unit.modules.utils import set_module_args
from .om_module import TestOmModule, load_fixture


class TestOmGroupsModule(TestOmModule):

    module = om_groups

    def setUp(self):
        super(TestOmGroupsModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "facts.groups.groups.GroupsFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestOmGroupsModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("om_groups_config.cfg")
        self.get_device_data.side_effect = load_from_file

    def test_om_groups_merged(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'ansible-test',
                    'description': 'Test group',
                    'enabled': True,
                    'access_rights': ['admin'],
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'groups/',
                'data': {
                    'group': {
                        'groupname': 'ansible-test',
                        'description': 'Test group',
                        'enabled': True,
                        'access_rights': ['admin'],
                    }
                },
                'method': 'POST'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_groups_merged_idempotent(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'admin',
                    'description': 'Provides users with unlimited configuration and management privileges',
                    'enabled': True,
                    'access_rights': ['admin'],
                }
            ],
            'state': 'merged',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_groups_deleted(self):
        set_module_args({
            'config': [
                {'groupname': 'netgrp'}
            ],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'groups/groups-2',
                'data': None,
                'method': 'DELETE'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_groups_deprecated_role_warning(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'ansible-test',
                    'description': 'Test group',
                    'enabled': True,
                    'role': 'Administrator',
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertIn(
            "The 'role' field is deprecated since 2022/08. Use 'access_rights' instead.",
            result['warnings']
        )

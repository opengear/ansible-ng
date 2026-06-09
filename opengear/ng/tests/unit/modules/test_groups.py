# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import groups
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestGroupsModule(TestModuleBase):

    module = groups

    def setUp(self):
        super(TestGroupsModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.groups.GroupsFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestGroupsModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("groups_config.cfg")
        self.get_device_data.side_effect = load_from_file

    def test_groups_create_merged(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'ansible-create',
                    'description': 'Test group created by Ansible',
                    'enabled': True,
                    'access_rights': ['pmshell'],
                    'ports': ['ports-1', 'ports-3']
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'groups/',
                'data': {
                    'group': {
                        'groupname': 'ansible-create',
                        'description': 'Test group created by Ansible',
                        'enabled': True,
                        'access_rights': ['pmshell'],
                        'ports': ['ports-1', 'ports-3'],
                    }
                },
                'method': 'POST'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_groups_create_merged_idempotent(self):
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

    # modify existing group with updated ports and rights list via merge
    def test_groups_update_merged(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'ansible-test',
                    'access_rights': ['web_ui'],
                    'ports': ['ports-6'],
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'groups/groups-3',
                'data': {
                    'group': {
                        'groupname': 'ansible-test',
                        'description': 'Test group',
                        'enabled': True,
                        'access_rights': ['pmshell', 'web_ui'],
                        'ports': ['ports-1', 'ports-2', 'ports-6'],
                        'members': [],
                        'role': 'ConsoleUser',
                        'mode': 'scoped',
                    }
                },
                'method': 'PUT'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # modify existing group with updated ports and rights list via replace
    def test_groups_update_replaced(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'ansible-test',
                    'description': 'Test group',
                    'enabled': True,
                    'access_rights': ['web_ui'],
                    'ports': ['ports-1'],
                }
            ],
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'groups/groups-3',
                'data': {
                    'group': {
                        'groupname': 'ansible-test',
                        'description': 'Test group',
                        'enabled': True,
                        'access_rights': ['web_ui',],
                        'ports': ['ports-1'],
                        'members': None,
                        'mode': None,
                        'role': None,
                    }
                },
                'method': 'PUT'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # override existing groups list with provided groups
    def test_groups_update_overridden(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'admin',
                    'description': 'Overridden groups, only admin remains',
                    'enabled': True,
                    'access_rights': ['admin'],
                    'ports': [],
                }
            ],
            'state': 'overridden',
        })

        commands = [
            {
                'path': 'groups/groups-2',
                'data': None,
                'method': 'DELETE'
            },
            {
                'path': 'groups/groups-3',
                'data': None,
                'method': 'DELETE'
            },
            {
                'path': 'groups/groups-1',
                'data': {
                    'group': {
                        'groupname': 'admin',
                        'description': 'Overridden groups, only admin remains',
                        'enabled': True,
                        'access_rights': ['admin'],
                        'ports': [],
                        'members': None,
                        'mode': None,
                        'role': None,
                    }
                },
                'method': 'PUT'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_groups_deleted(self):
        set_module_args({
            'config': [
                {'groupname': 'ansible-test'}
            ],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'groups/groups-3',
                'data': None,
                'method': 'DELETE'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_groups_deprecated_role_warning(self):
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

    def test_groups_rendered(self):
        set_module_args({
            'config': [
                {
                    'groupname': 'ansible-test',
                    'description': 'Test group',
                    'enabled': True,
                    'access_rights': ['pmshell'],
                    'ports': ['ports-1', 'ports-2'],
                }
            ],
            'state': 'rendered',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_groups_gathered(self):
        set_module_args({
            'state': 'gathered',
        })

        result = self.execute_module(changed=False)

        self.assertIn('gathered', result)
        groups = result['gathered']
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0]['groupname'], 'admin')
        self.assertEqual(groups[1]['groupname'], 'netgrp')
        self.assertEqual(groups[2]['groupname'], 'ansible-test')

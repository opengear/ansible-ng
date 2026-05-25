# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.om.tests.unit.compat.mock import patch
from ansible_collections.opengear.om.plugins.modules import om_users
from ansible_collections.opengear.om.tests.unit.modules.utils import set_module_args
from .om_module import TestOmModule, load_fixture


class TestOmUsersModule(TestOmModule):

    module = om_users

    def setUp(self):
        super(TestOmUsersModule, self).setUp()
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
        super(TestOmUsersModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("om_users_config.cfg")

        self.get_device_data.side_effect = load_from_file

    def test_om_users_merged(self):
        set_module_args({
            'config': [
                {
                    'id': 'users-1',
                    'username': 'user1-modified',
                    'description': 'This user was changed',
                    'enabled': False,
                    'no_password': True,
                    'groups': ['g2']
                },
                {
                    'username': 'user3',
                    'description': 'This user was added',
                    'enabled': True,
                    'no_password': True,
                    'groups': ['g1']
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'users/users-1',
                'data': {
                    'user': {
                        'username': 'user1-modified',
                        'description': 'This user was changed',
                        'enabled': False,
                        'no_password': True,
                        'ssh_password_enabled': True,
                        'groups': ['g1', 'g2']
                    }
                },
                'method': 'PUT'
            },
            {
                'path': 'users/',
                'data': {
                    'user': {
                        'username': 'user3',
                        'description': 'This user was added',
                        'enabled': True,
                        'no_password': True,
                        'groups': ['g1']
                    }
                },
                'method': 'POST'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_users_merged_idempotent(self):
        set_module_args({
            'config': [
                {
                    'username': "user1",
                    'enabled': True,
                    'hashed_password': (
                        "{{ 'hash' }}"
                    ),
                    'groups': ["g1"]
                },
                {
                    'username': "user2",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "merged",
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_users_replaced(self):
        set_module_args({
            'config': [
                {
                    'id': "users-1",
                    'username': "user1-modified",
                    'description': "This user was changed",
                    'enabled': False,
                    'no_password': True,
                    'groups': ["g2"]
                },
                {
                    'username': "user3",
                    'description': "This user was added",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "replaced",
        })

        commands = [
            {
                'path': 'users/users-1',
                'data': {
                    'user': {
                        'username': "user1-modified",
                        'description': "This user was changed",
                        'enabled': False,
                        'no_password': True,
                        'groups': ["g2"]
                    }
                },
                'method': 'PUT'
            },
            {
                'path': 'users/',
                'data': {
                    'user': {
                        'username': "user3",
                        'description': "This user was added",
                        'enabled': True,
                        'no_password': True,
                        'groups': ["g1"]
                    }
                },
                'method': 'POST'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_users_replaced_idempotent(self):
        set_module_args({
            'config': [
                {
                    'username': "user1",
                    'enabled': True,
                    'hashed_password': (
                        "{{ 'hash' }}"
                    ),
                    'groups': ["g1"]
                },
                {
                    'username': "user2",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "replaced",
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_users_overridden(self):
        set_module_args({
            'config': [
                {
                    'id': "users-1",
                    'username': "user1-modified",
                    'description': "This user was changed",
                    'enabled': False,
                    'no_password': True,
                    'groups': ["g2"]
                },
                {
                    'username': "user3",
                    'description': "This user was added",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "overridden",
        })

        commands = [
            {'path': 'users/users-2', 'data': None, 'method': 'DELETE'},
            {
                'path': 'users/users-1',
                'data': {
                    'user': {
                        'username': "user1-modified",
                        'description': "This user was changed",
                        'enabled': False,
                        'no_password': True,
                        'groups': ["g2"]
                    }
                },
                'method': 'PUT'
            },
            {
                'path': 'users/',
                'data': {
                    'user': {
                        'username': "user3",
                        'description': "This user was added",
                        'enabled': True,
                        'no_password': True,
                        'groups': ["g1"]
                    }
                },
                'method': 'POST'
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_users_overridden_idempotent(self):
        set_module_args({
            'config': [
                {
                    'username': "user1",
                    'enabled': True,
                    'hashed_password': (
                        "{{ 'hash' }}"
                    ),
                    'groups': ["g1"]
                },
                {
                    'username': "user2",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "overridden",
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_users_deleted(self):
        set_module_args({
            'config': [
                {'id': "users-1"},
                {'username': "user2"},
                {'username': "user3"}
            ],
            'state': "deleted",
        })

        commands = [
            {
                'path': 'users/users-2',
                'data': None,
                'method': 'DELETE'
            }
        ]

        self.execute_module(changed=True, commands=commands)

    def test_om_users_rendered(self):
        set_module_args({
            'config': [
                {
                    'id': "users-1",
                    'username': "user1-modified",
                    'description': "This user was changed",
                    'enabled': False,
                    'no_password': True,
                    'groups': ["g2"]
                },
                {
                    'username': "user3",
                    'description': "This user was added",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "rendered",
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_users_gathered(self):
        set_module_args({
            'config': [
                {
                    'id': "users-1",
                    'username': "user1-modified",
                    'description': "This user was changed",
                    'enabled': False,
                    'no_password': True,
                    'groups': ["g2"]
                },
                {
                    'username': "user3",
                    'description': "This user was added",
                    'enabled': True,
                    'no_password': True,
                    'groups': ["g1"]
                }
            ],
            'state': "gathered",
        })

        commands = []

        self.execute_module(changed=False, commands=commands)

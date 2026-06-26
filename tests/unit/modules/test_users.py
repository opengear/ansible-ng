# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import users
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestUsersModule(TestModuleBase):

    module = users

    def setUp(self):
        super(TestUsersModule, self).setUp()
        self.maxDiff = None

        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.users.UsersFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestUsersModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        def load_from_file(*args, **kwargs):
            return load_fixture("users_config.cfg")

        self.get_device_data.side_effect = load_from_file

    def test_users_merged(self):
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

    def test_users_merged_idempotent(self):
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

    def test_users_replaced(self):
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

    def test_users_replaced_idempotent(self):
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

    def test_users_overridden(self):
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

    def test_users_overridden_idempotent(self):
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

    def test_users_deleted(self):
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

    def test_users_rendered(self):
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

    def test_users_gathered(self):
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

    # --- password handling ---
    def test_users_merged_plaintext_password_strips_hashed(self):
        """When providing a plaintext password, hashed_password from device should be stripped"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'password': 'NewP@ss123',
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        # Verify hashed_password is not in the PUT payload
        self.assertEqual(len(result['commands']), 1)
        payload = result['commands'][0]['data']['user']
        self.assertIn('password', payload)
        self.assertNotIn('hashed_password', payload)

    def test_users_merged_no_password_strips_both(self):
        """When no_password is true, both password fields should be stripped"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'no_password': True,
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        payload = result['commands'][0]['data']['user']
        self.assertNotIn('password', payload)
        self.assertNotIn('hashed_password', payload)

    def test_users_merged_no_password_change_preserves_idempotency(self):
        """Merging without specifying a password should not trigger a change if other fields match"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'enabled': True,
                    'groups': ['g1'],
                }
            ],
            'state': 'merged',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

        # --- check mode ---
        def test_users_check_mode(self):
            set_module_args({
                '_ansible_check_mode': True,
                'config': [
                    {
                        'username': 'user1',
                        'description': 'This user was changed',
                        'enabled': False,
                    }
                ],
                'state': 'merged',
            })

            result = self.execute_module(changed=True)
            self.assertEqual(len(result['commands']), 1)
            self.connection.return_value.send_request.assert_not_called()

    # --- diff mode ---
    def test_users_diff_merged_update(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'username': 'user1',
                    'description': 'This user was changed',
                    'enabled': False,
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
        self.assertEqual(before[0]['username'], 'user1')
        self.assertEqual(after[0]['username'], 'user1')
        self.assertEqual(after[0]['enabled'], False)
        self.assertEqual(after[0]['description'], 'This user was changed')

    def test_users_diff_deleted(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {'username': 'user2'}
            ],
            'state': 'deleted',
        })

        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 1)
        self.assertEqual(before[0]['username'], 'user2')
        self.assertEqual(after[0], {})

    def test_users_diff_overridden(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'username': 'user1',
                    'enabled': True,
                    'no_password': True,
                    'groups': ['g1'],
                }
            ],
            'state': 'overridden',
        })

        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 2)
        self.assertEqual(len(after), 2)
        deleted_usernames = {u['username'] for u in before if u.get('username') not in
                             {u.get('username') for u in after if u}}
        self.assertIn('user2', deleted_usernames)

    def test_users_no_diff_when_not_requested(self):
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'description': 'This user was changed',
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_users_no_diff_when_idempotent(self):
        set_module_args({
            '_ansible_diff': True,
            'config': [
                {
                    'username': 'user1',
                    'enabled': True,
                    'hashed_password': "{{ 'hash' }}",
                    'groups': ['g1'],
                }
            ],
            'state': 'merged',
        })

        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    # --- check mode + diff ---
    def test_users_check_mode_with_diff_merged(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {
                    'username': 'user1',
                    'description': 'This user was changed',
                    'enabled': False,
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
        self.assertEqual(before[0]['username'], 'user1')
        self.assertEqual(after[0]['enabled'], False)
        self.assertNotEqual(before[0]['enabled'], after[0]['enabled'])

    def test_users_check_mode_with_diff_deleted(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {'username': 'user2'}
            ],
            'state': 'deleted',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before[0]['username'], 'user2')
        self.assertEqual(after[0], {})

    def test_users_check_mode_with_diff_overridden(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {
                    'username': 'user1',
                    'enabled': True,
                    'no_password': True,
                    'groups': ['g1'],
                }
            ],
            'state': 'overridden',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 2)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(len(before), 2)
        deleted_usernames = {u['username'] for u in before if u.get('username') not in
                             {u.get('username') for u in after if u}}
        self.assertIn('user2', deleted_usernames)

    def test_users_check_mode_with_diff_replaced(self):
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': [
                {
                    'username': 'user1',
                    'enabled': False,
                    'no_password': True,
                    'groups': ['g2'],
                }
            ],
            'state': 'replaced',
        })

        result = self.execute_module(changed=True)
        self.assertEqual(len(result['commands']), 1)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertEqual(before[0]['username'], 'user1')
        self.assertEqual(after[0]['enabled'], False)
        self.assertNotIn('g1', after[0].get('groups', []))
        self.assertIn('g2', after[0].get('groups', []))

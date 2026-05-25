# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.om.tests.unit.compat.mock import patch
from ansible_collections.opengear.om.plugins.modules import om_user_authorized_keys
from ansible_collections.opengear.om.tests.unit.modules.utils import set_module_args
from .om_module import TestOmModule, load_fixture


class TestOmUserAuthorizedKeysModule(TestOmModule):

    module = om_user_authorized_keys

    def setUp(self):
        super(TestOmUserAuthorizedKeysModule, self).setUp()
        self.maxDiff = None

        # Mock the users lookup (get_users) used to build username -> user_id map
        self.mock_get_users = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "facts.user_authorized_keys.user_authorized_keys.UserAuthorizedKeysFacts.get_users"
        )
        self.get_users = self.mock_get_users.start()

        # Mock the per-user key fetch
        self.mock_get_device_data = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "facts.user_authorized_keys.user_authorized_keys.UserAuthorizedKeysFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.om.plugins.module_utils.network.om."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestOmUserAuthorizedKeysModule, self).tearDown()
        self.mock_get_users.stop()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        fixture = load_fixture("om_user_authorized_keys_config.cfg")

        # get_users returns a list of {username, id} dicts
        self.get_users.return_value = [
            {'username': entry['username'], 'id': entry['user_id']}
            for entry in fixture
        ]

        # get_device_data is called per user_id, return that user's keys
        key_map = {entry['user_id']: entry['keys'] for entry in fixture}

        def load_keys_for_user(*args, **kwargs):
            user_id = [k for k in key_map if k in args[1]][0]
            return key_map[user_id]

        self.get_device_data.side_effect = load_keys_for_user

    # --- merged ---
    def test_om_user_authorized_keys_merged_add_key(self):
        """Add a new key to a user that already has keys"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c user1@laptop',
                        'ssh-rsa AAAAB3NzaC1yc2NEWKEY user1@newhost',
                    ]
                }
            ],
            'state': 'merged',
        })

        commands = [
            {
                'path': 'users/users-1/ssh/authorized_keys',
                'data': {'authorized_key': {'key': 'ssh-rsa AAAAB3NzaC1yc2NEWKEY user1@newhost'}},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_user_authorized_keys_merged_idempotent(self):
        """Merging keys already present should produce no commands"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c user1@laptop',
                    ]
                }
            ],
            'state': 'merged',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_user_authorized_keys_merged_new_user(self):
        """Add keys to a user that has no existing keys"""
        set_module_args({
            'config': [
                {
                    'username': 'user2',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2NEWKEY user2@laptop',
                    ]
                }
            ],
            'state': 'merged',
        })
 
        commands = [
            {
                'path': 'users/users-2/ssh/authorized_keys',
                'data': {'authorized_key': {'key': 'ssh-rsa AAAAB3NzaC1yc2NEWKEY user2@laptop'}},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- replaced ---
    def test_om_user_authorized_keys_replaced(self):
        """Replace all keys for a user - removes old keys, adds new ones"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2NEWKEY user1@newhost',
                    ]
                }
            ],
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'users/users-1/ssh/authorized_keys/users_ssh_authorized_keys-1',
                'data': None,
                'method': 'DELETE',
            },
            {
                'path': 'users/users-1/ssh/authorized_keys/users_ssh_authorized_keys-2',
                'data': None,
                'method': 'DELETE',
            },
            {
                'path': 'users/users-1/ssh/authorized_keys',
                'data': {'authorized_key': {'key': 'ssh-rsa AAAAB3NzaC1yc2NEWKEY user1@newhost'}},
                'method': 'POST',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_user_authorized_keys_replaced_idempotent(self):
        """Replacing with the same keys should produce no commands"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c user1@laptop',
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp user1@workstation',
                    ]
                }
            ],
            'state': 'replaced',
        })
 
        commands = []
        self.execute_module(changed=False, commands=commands)

    # --- deleted ---
    def test_om_user_authorized_keys_deleted(self):
        """Delete a specific key from a user"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c user1@laptop',
                    ]
                }
            ],
            'state': 'deleted',
        })
 
        commands = [
            {
                'path': 'users/users-1/ssh/authorized_keys/users_ssh_authorized_keys-1',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_om_user_authorized_keys_deleted_idempotent(self):
        """Deleting a key that doesn't exist should produce no commands"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2NONEXISTENT user1@ghost',
                    ]
                }
            ],
            'state': 'deleted',
        })

        commands = []
        self.execute_module(changed=False, commands=commands)

    def test_om_user_authorized_keys_deleted_all(self):
        """Delete all keys for a user"""
        set_module_args({
            'config': [
                {
                    'username': 'user1',
                    'keys': [
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c user1@laptop',
                        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp user1@workstation',
                    ]
                }
            ],
            'state': 'deleted',
        })

        commands = [
            {
                'path': 'users/users-1/ssh/authorized_keys/users_ssh_authorized_keys-1',
                'data': None,
                'method': 'DELETE',
            },
            {
                'path': 'users/users-1/ssh/authorized_keys/users_ssh_authorized_keys-2',
                'data': None,
                'method': 'DELETE',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- gathered ---
    def test_om_user_authorized_keys_gathered(self):
        """Gathered state returns current authorized keys structured by user"""
        set_module_args({
            'state': 'gathered',
        })
 
        result = self.execute_module(changed=False)
 
        self.assertIn('gathered', result)
        gathered = result['gathered']
        self.assertEqual(len(gathered), 2)
        self.assertEqual(gathered[0]['username'], 'user1')
        self.assertEqual(len(gathered[0]['keys']), 2)
        self.assertEqual(gathered[1]['username'], 'user2')
        self.assertEqual(len(gathered[1]['keys']), 0)

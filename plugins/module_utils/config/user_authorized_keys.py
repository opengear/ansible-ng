# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy
import json

from ansible.module_utils.connection import ConnectionError

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.facts import Facts
from ansible_collections.opengear.ng.plugins.module_utils.utils.utils import (
    to_list,
)


class UserAuthorizedKeys(ConfigBase):
    """
    The user_authorized_keys class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'user_authorized_keys',
    ]

    def __init__(self, module):
        super(UserAuthorizedKeys, self).__init__(module)

    def get_user_authorized_keys_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A list
        :returns: The current configuration as a list
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        facts_data = facts['ansible_network_resources'].get('user_authorized_keys')
        if not facts_data:
            return []
        return facts_data

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        # ----------------------
        # Get facts
        # ----------------------
        if self.state in self.ACTION_STATES or self.state == 'gathered':
            existing_facts = self.get_user_authorized_keys_facts()
        else:
            existing_facts = []
        # ----------------------
        # Prepare commands
        # ----------------------
        if self.state in self.ACTION_STATES:
            commands.extend(self.set_config(existing_facts))
        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    try:
                        self._connection.send_request(command['data'], command['path'], command['method'])
                    except ConnectionError as exc:
                        if not exc.args[0].startswith('Expecting value:'):
                            raise exc
            result['changed'] = True

            if self._module._diff:
                result['diff'] = self._build_diff(commands, existing_facts)
        # --------------------------
        # Prepare result
        # --------------------------
        result['commands'] = commands

        if self.state in self.ACTION_STATES:
            changed_facts = self.get_user_authorized_keys_facts()
            result['before'] = existing_facts
            if result['changed']:
                result['after'] = changed_facts
        elif self.state == 'gathered':
            result['gathered'] = existing_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a list
        :param have: the current configuration as a list
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        # Build lookup maps from have:
        # username -> user_id
        # username -> {key_string -> key_id}
        username_id_map = {}
        username_keys_map = {}

        for entry in have:
            username = entry['username']
            username_id_map[username] = entry['user_id']
            username_keys_map[username] = {
                k['key']: k['id'] for k in entry.get('keys', [])
            }

        state = self._module.params['state']
        if state == 'deleted':
            commands = self._state_deleted(want, username_id_map, username_keys_map)
        elif state == 'merged':
            commands = self._state_merged(want, username_id_map, username_keys_map)
        elif state == 'replaced':
            commands = self._state_replaced(want, username_id_map, username_keys_map)
        else:
            commands = []
        return commands

    @staticmethod
    def _build_diff(commands, existing_facts):
        """ Build a before/after diff scoped to users whose keys changed.

        :param commands: the list of commands that will be (or would be) sent
        :param existing_facts: the current authorized keys facts
        :rtype: dict
        :returns: a dict with 'before' and 'after' keys, each a JSON string
                  showing only the users whose keys are affected
        """
        # Build a lookup of existing key lists by username, keyed by user_id
        # so commands (which reference user_id in the path) can be matched
        # back to a username.
        user_id_to_username = {entry['user_id']: entry['username'] for entry in existing_facts}
        before_keys = {entry['username']: list(k['key'] for k in entry.get('keys', [])) for entry in existing_facts}
        after_keys = deepcopy(before_keys)

        affected_usernames = set()

        for command in commands:
            # path is one of:
            #   users/{user_id}/ssh/authorized_keys           (POST)
            #   users/{user_id}/ssh/authorized_keys/{key_id}   (DELETE)
            parts = command['path'].split('/')
            user_id = parts[1]
            username = user_id_to_username.get(user_id)
            if not username:
                continue
            affected_usernames.add(username)

            if command['method'] == 'POST':
                key = command['data']['authorized_key']['key']
                after_keys.setdefault(username, [])
                if key not in after_keys[username]:
                    after_keys[username].append(key)
            elif command['method'] == 'DELETE':
                key_id = parts[-1]
                # Find the key string matching this key_id from existing facts
                entry = next((e for e in existing_facts if e['username'] == username), None)
                if entry:
                    key = next((k['key'] for k in entry.get('keys', []) if k['id'] == key_id), None)
                    if key and key in after_keys.get(username, []):
                        after_keys[username].remove(key)

        diff_before = [
            {'username': u, 'keys': before_keys.get(u, [])}
            for u in affected_usernames
        ]
        diff_after = [
            {'username': u, 'keys': after_keys.get(u, [])}
            for u in affected_usernames
        ]

        return {
            'before': json.dumps(diff_before, indent=4) + '\n',
            'after': json.dumps(diff_after, indent=4) + '\n',
        }

    @staticmethod
    def _state_merged(want, username_id_map, username_keys_map):
        """ The command generator when state is merged

        Adds keys not already present. Existing keys are preserved.

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        for entry in want:
            username = entry['username']
            user_id = username_id_map.get(username)
            if not user_id:
                raise ValueError(f"User '{username}' not found. Ensure the user exists before managing authorized keys.")

            existing_keys = username_keys_map.get(username, {})
            for key in entry.get('keys', []):
                if key not in existing_keys:
                    commands.append({
                        'path': f'users/{user_id}/ssh/authorized_keys',
                        'data': {'authorized_key': {'key': key}},
                        'method': 'POST',
                    })
        return commands

    @staticmethod
    def _state_replaced(want, username_id_map, username_keys_map):
        """ The command generator when state is replaced

        Replaces all keys for the user with only those specified.
        Keys not in want are deleted. Keys not yet present are added.

        :rtype: A list
        :returns: the commands necessary to replace the current configuration
        """
        commands = []
        for entry in want:
            username = entry['username']
            user_id = username_id_map.get(username)
            if not user_id:
                raise ValueError(f"User '{username}' not found. Ensure the user exists before managing authorized keys.")

            want_keys = set(entry.get('keys', []))
            existing_keys = username_keys_map.get(username, {})

            # DELETE keys not in want
            for key, key_id in existing_keys.items():
                if key not in want_keys:
                    commands.append({
                        'path': f'users/{user_id}/ssh/authorized_keys/{key_id}',
                        'data': None,
                        'method': 'DELETE',
                    })

            # POST keys not already present
            for key in want_keys:
                if key not in existing_keys:
                    commands.append({
                        'path': f'users/{user_id}/ssh/authorized_keys',
                        'data': {'authorized_key': {'key': key}},
                        'method': 'POST',
                    })
        return commands

    @staticmethod
    def _state_deleted(want, username_id_map, username_keys_map):
        """ The command generator when state is deleted

        Removes the specified keys from the user.

        :rtype: A list
        :returns: the commands necessary to delete the specified keys
        """
        commands = []
        for entry in want:
            username = entry['username']
            user_id = username_id_map.get(username)
            if not user_id:
                raise ValueError(f"User '{username}' not found. Ensure the user exists before managing authorized keys.")

            existing_keys = username_keys_map.get(username, {})
            for key in entry.get('keys', []):
                key_id = existing_keys.get(key)
                if key_id:
                    commands.append({
                        'path': f'users/{user_id}/ssh/authorized_keys/{key_id}',
                        'data': None,
                        'method': 'DELETE',
                    })
                # if key not found in have, nothing to delete (idempotent)
        return commands

#!/usr/bin/python
# -*- coding: utf-8 -*-

from copy import deepcopy
from ansible.module_utils.connection import ConnectionError
from ansible_collections.opengear.om.plugins.module_utils.network.om.facts.facts import Facts
from ansible_collections.opengear.om.plugins.module_utils.network.om.config.base import ConfigBase
from ansible_collections.opengear.om.plugins.module_utils.network.om.utils.utils import to_list


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

        if self.state in self.ACTION_STATES or self.state == 'gathered':
            existing_facts = self.get_user_authorized_keys_facts()
            if self.state != 'gathered':
                commands.extend(self.set_config(existing_facts))
        else:
            existing_facts = []

        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    try:
                        self._connection.send_request(command['data'], command['path'], command['method'])
                    except ConnectionError as exc:
                        if not exc.args[0].startswith('Expecting value:'):
                            raise exc
            result['changed'] = True

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

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
    command_builder,
    dict_merge,
    find_instance_id,
    is_subset,
    remove_empties,
    to_list,
)


class Users(ConfigBase):
    """
    Manages configuration of users on Opengear devices
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'users',
    ]

    def __init__(self, module):
        super(Users, self).__init__(module)
        self.current_state = {}

    def get_users_facts(self, data=None):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources, data)
        users_facts = facts['ansible_network_resources'].get('users')
        if not users_facts:
            return []
        return users_facts

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
        if self.state in self.ACTION_STATES:
            existing_users_facts = self.get_users_facts()
        else:
            existing_users_facts = {}
        # -----------------------
        # Prepare commands
        # -----------------------
        if self.state in self.ACTION_STATES or self.state == 'rendered':
            commands.extend(self.set_config(existing_users_facts, warnings))
        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    user_id = None
                    if command['method'] in ['PUT', 'DELETE']:
                        user_id = command['path'].split('/')[-1]
                    try:
                        response = self._connection.send_request(command['data'], command['path'], command['method'])
                        if command['method'] == 'DELETE':
                            # Delete returns no response body
                            self.current_state.pop(user_id, None)
                        elif user_id and command['method'] == 'PUT':
                            self.current_state[user_id] = response['user']
                        else:
                            self.current_state[response['user']['id']] = response['user']
                    except ConnectionError as exc:
                        if not exc.args[0].startswith('Expecting value:'):
                            raise exc
                        self.current_state.pop(user_id, None)
            else:
                # Simulate state changes for check mode + diff
                for command in commands:
                    if command['method'] == 'DELETE':
                        user_id = command['path'].split('/')[-1]
                        self.current_state.pop(user_id, None)
                    elif command['method'] == 'PUT':
                        user_id = command['path'].split('/')[-1]
                        if user_id in self.current_state:
                            self.current_state[user_id].update(command['data']['user'])
                    elif command['method'] == 'POST':
                        data = command['data']['user']
                        temp_key = f"check-{data['username']}"
                        self.current_state[temp_key] = data
            result['changed'] = True
        # --------------------------
        # Prepare result
        # --------------------------
        result['commands'] = commands
        if self.state in self.ACTION_STATES or self.state == 'gathered':
            changed_users_facts = self.get_users_facts(self.current_state.values())
        elif self.state == 'rendered':
            result['rendered'] = commands
        if self.state in self.ACTION_STATES:
            result['before'] = existing_users_facts
            if result['changed']:
                result['after'] = changed_users_facts
                # Prepare diff output
                if self._module._diff:
                    diff_before = []
                    diff_after = []

                    # Build a lookup of existing users by id
                    existing_by_id = {u['id']: u for u in existing_users_facts}

                    for command in commands:
                        if command['method'] == 'DELETE':
                            user_id = command['path'].split('/')[-1]
                            if user_id in existing_by_id:
                                diff_before.append(existing_by_id[user_id])
                                diff_after.append({})
                        elif command['method'] == 'PUT':
                            user_id = command['path'].split('/')[-1]
                            if user_id in existing_by_id:
                                before = existing_by_id[user_id]
                                after = {**before, **command['data']['user']}
                                diff_before.append(before)
                                diff_after.append(after)
                        elif command['method'] == 'POST':
                            diff_before.append({})
                            diff_after.append(command['data']['user'])

                    result['diff'] = {
                        'before': json.dumps(diff_before, indent=4) + '\n',
                        'after': json.dumps(diff_after, indent=4) + '\n',
                    }
        elif self.state == 'gathered':
            result['gathered'] = changed_users_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_users_facts, warnings):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_users_facts
        resp = self.set_state(want, have, warnings)
        return to_list(resp)

    def set_state(self, want, have, warnings):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        username_id_map = {}
        id_user_map = {}
        for user in have:
            username_id_map[user['username']] = user['id']
            id_user_map[user['id']] = user

        state = self._module.params['state']
        if state == 'overridden':
            commands = self._state_overridden(want, username_id_map, id_user_map)
        elif state == 'deleted':
            commands = self._state_deleted(want, username_id_map)
        elif state == 'merged':
            commands = self._state_merged(want, username_id_map, id_user_map)
        elif state == 'replaced':
            commands = self._state_replaced(want, username_id_map, id_user_map)
        else:
            commands = []
        return commands

    @staticmethod
    def _state_replaced(want, username_id_map, id_user_map):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        for user in want:
            user_id = find_instance_id(username_id_map, 'username', user)
            user = remove_empties(user)
            if user_id in id_user_map:
                data = deepcopy(user)
                data['id'] = user_id
                data_compare = {k: v for k, v in data.items() if k not in ('hashed_password', 'password')}
                device_compare = {k: v for k, v in remove_empties(id_user_map[user_id]).items() if k not in ('hashed_password', 'password')}
                if is_subset(data_compare, device_compare):
                    continue
                if 'groups' not in data or data['groups'] is None:
                    data['groups'] = []
                if data.get('no_password'):
                    data.pop('hashed_password', None)
                    data.pop('password', None)
                # read-only fields, never send to API
                data.pop('groupNames', None)
            else:
                data = user
            data.pop('id', None)
            command = command_builder({'user': data}, 'users/', user_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_overridden(want, username_id_map, id_user_map):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        deleted_users = deepcopy(id_user_map)

        for user in want:
            if 'id' in user and user['id'] in id_user_map:
                user_id = user['id']
            else:
                user_id = find_instance_id(username_id_map, 'username', user)
            if user_id in deleted_users:
                deleted_users.pop(user_id)
        commands.extend(Users._state_deleted(deleted_users.values(), username_id_map))

        commands.extend(Users._state_replaced(want, username_id_map, id_user_map))
        return commands

    @staticmethod
    def _state_merged(want, username_id_map, id_user_map):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        for user in want:
            data = remove_empties(user)
            user_id = find_instance_id(username_id_map, 'username', data)
            user_provided_password = 'password' in data    # password is intentionally being set
            if user_id in id_user_map:
                device_user = deepcopy(id_user_map[user_id])
                merged_data = dict_merge(device_user, data)
                data_compare = {k: v for k, v in merged_data.items() if k not in ('hashed_password', 'password')}
                device_compare = {k: v for k, v in device_user.items() if k not in ('hashed_password', 'password')}
                if is_subset(data_compare, device_compare) and not user_provided_password:
                    continue
                else:
                    data = merged_data
                if user_provided_password:
                    # exclude the existing hashed password from merge if being set
                    data.pop('hashed_password', None)
                # read-only fields, never send to API
                data.pop('id', None)
                data.pop('groupNames', None)
            else:
                user_id = None
            if data.get('no_password'):
                data.pop('hashed_password', None)
                data.pop('password', None)
            command = command_builder({'user': data}, 'users/', user_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_deleted(want, username_id_map):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        for user in want:
            user_id = find_instance_id(username_id_map, 'username', user)
            command = command_builder(None, 'users/', user_id, ['users-1'])
            if command:
                commands.append(command)
        return commands

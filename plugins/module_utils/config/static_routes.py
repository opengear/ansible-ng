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
    dict_diff,
    dict_merge,
    find_instance_id,
    is_subset,
    remove_empties,
    to_list,
)


class StaticRoutes(ConfigBase):
    """
    Manages configuration of static routes on Opengear devices
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'static_routes',
    ]

    def __init__(self, module):
        super(StaticRoutes, self).__init__(module)
        self.current_state = {}

    def get_static_routes_facts(self, data=None):
        """ Get the 'facts' (the current configuration)

        :rtype: A list
        :returns: The current configuration as a list
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources, data)
        static_routes_facts = facts['ansible_network_resources'].get('static_routes')
        if not static_routes_facts:
            return []
        return static_routes_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES:
            existing_static_routes_facts = self.get_static_routes_facts()
        else:
            existing_static_routes_facts = {}
        if self.state in self.ACTION_STATES or self.state == 'rendered':
            commands.extend(self.set_config(existing_static_routes_facts, warnings))
        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    route_id = None
                    if command['method'] in ['PUT', 'DELETE'] and '/' in command['path'].rstrip('/'):
                        parts = command['path'].rstrip('/').split('/')
                        if parts[-1] != 'static_routes':
                            route_id = parts[-1]
                    try:
                        response = self._connection.send_request(command['data'], command['path'], command['method'])
                        if command['method'] == 'DELETE':
                            self.current_state.pop(route_id, None)
                        elif route_id and command['method'] == 'PUT':
                            self.current_state[route_id] = response['static_route']
                        elif command['method'] == 'PUT' and command['path'].rstrip('/').endswith('static_routes'):
                            # Bulk PUT (overridden)
                            self.current_state = {r['id']: r for r in response.get('static_routes', [])}
                        else:
                            self.current_state[response['static_route']['id']] = response['static_route']
                    except ConnectionError as exc:
                        if not exc.args[0].startswith('Expecting value:'):
                            raise exc
                        if route_id:
                            self.current_state.pop(route_id, None)
            else:
                # Simulate state changes for check mode + diff
                for command in commands:
                    if command['method'] == 'DELETE':
                        parts = command['path'].rstrip('/').split('/')
                        route_id = parts[-1]
                        self.current_state.pop(route_id, None)
                    elif command['method'] == 'PUT':
                        parts = command['path'].rstrip('/').split('/')
                        if parts[-1] != 'static_routes':
                            route_id = parts[-1]
                            if route_id in self.current_state:
                                self.current_state[route_id].update(command['data']['static_route'])
                        else:
                            # Bulk PUT (overridden)
                            new_routes = command['data'].get('static_routes', [])
                            self.current_state = {}
                            for i, r in enumerate(new_routes):
                                temp_key = 'check-{0}'.format(i)
                                self.current_state[temp_key] = r
                    elif command['method'] == 'POST':
                        data = command['data']['static_route']
                        temp_key = 'check-{0}'.format(data.get('destination_address', ''))
                        self.current_state[temp_key] = data
            result['changed'] = True

        result['commands'] = commands
        if self.state in self.ACTION_STATES or self.state == 'gathered':
            changed_static_routes_facts = self.get_static_routes_facts(self.current_state.values())
        elif self.state == 'rendered':
            result['rendered'] = commands
        if self.state in self.ACTION_STATES:
            result['before'] = existing_static_routes_facts
            if result['changed']:
                result['after'] = changed_static_routes_facts
                if self._module._diff:
                    diff_before = []
                    diff_after = []

                    existing_by_id = {r['id']: r for r in existing_static_routes_facts}

                    for command in commands:
                        if command['method'] == 'DELETE':
                            route_id = command['path'].rstrip('/').split('/')[-1]
                            if route_id in existing_by_id:
                                diff_before.append(existing_by_id[route_id])
                                diff_after.append({})

                        elif command['method'] == 'PUT':
                            parts = command['path'].rstrip('/').split('/')
                            if parts[-1] != 'static_routes':
                                route_id = parts[-1]
                                if route_id in existing_by_id:
                                    before = existing_by_id[route_id]
                                    after = {**before, **command['data']['static_route']}
                                    diff_before.append(before)
                                    diff_after.append(after)
                            else:
                                # Bulk PUT (overridden)
                                diff_before.extend(existing_static_routes_facts)
                                diff_after.extend(command['data'].get('static_routes', []))

                        elif command['method'] == 'POST':
                            diff_before.append({})
                            diff_after.append(command['data']['static_route'])

                    result['diff'] = {
                        'before': json.dumps(diff_before, indent=4) + '\n',
                        'after': json.dumps(diff_after, indent=4) + '\n',
                    }
        elif self.state == 'gathered':
            result['gathered'] = changed_static_routes_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_static_routes_facts, warnings):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_static_routes_facts
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
        destination_id_map = {}
        id_route_map = {}
        for route in have:
            destination_id_map[route['destination_address']] = route['id']
            id_route_map[route['id']] = route

        self.current_state = deepcopy(id_route_map)

        state = self._module.params['state']
        if state == 'overridden':
            commands = self._state_overridden(want, destination_id_map, id_route_map)
        elif state == 'deleted':
            commands = self._state_deleted(want, destination_id_map)
        elif state == 'merged':
            commands = self._state_merged(want, destination_id_map, id_route_map)
        elif state == 'replaced':
            commands = self._state_replaced(want, destination_id_map, id_route_map)
        else:
            commands = []
        return commands

    @staticmethod
    def _state_replaced(want, destination_id_map, id_route_map):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        for route in want:
            route_id = find_instance_id(destination_id_map, 'destination_address', route)
            data = remove_empties(route)
            if route_id in id_route_map:
                data['id'] = route_id
                if is_subset(data, remove_empties(id_route_map[route_id])):
                    continue
                data.pop('id', None)
            command = command_builder({'static_route': data}, 'static_routes/', route_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_overridden(want, destination_id_map, id_route_map):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        if not want and not id_route_map:
            # There are no existing records and no desired records, no-op
            return commands

        deleted_routes = deepcopy(id_route_map)

        for route in want:
            if 'id' in route and route['id'] in id_route_map:
                route_id = route['id']
            else:
                route_id = find_instance_id(destination_id_map, 'destination_address', route)
            if route_id in deleted_routes:
                deleted_routes.pop(route_id)

        if len(deleted_routes) == len(id_route_map):
            clean_want = [remove_empties(r) for r in want]
            commands.append({'data': {'static_routes': clean_want}, 'path': 'static_routes/', 'method': 'PUT'})
        else:
            commands.extend(StaticRoutes._state_deleted(deleted_routes.values(), destination_id_map))
            commands.extend(StaticRoutes._state_replaced(want, destination_id_map, id_route_map))

        return commands

    @staticmethod
    def _state_merged(want, destination_id_map, id_route_map):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []
        for route in want:
            data = remove_empties(route)
            route_id = find_instance_id(destination_id_map, 'destination_address', data)
            if route_id in id_route_map:
                device_route = id_route_map[route_id]
                merged_data = dict_merge(device_route, data)
                if dict_diff(merged_data, device_route):
                    data = merged_data
                else:
                    continue
                data.pop('id', None)
            else:
                route_id = None
            command = command_builder({'static_route': data}, 'static_routes/', route_id)
            if command:
                commands.append(command)
        return commands

    @staticmethod
    def _state_deleted(want, destination_id_map):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []
        for route in want:
            route_id = find_instance_id(destination_id_map, 'destination_address', route)
            command = command_builder(None, 'static_routes/', route_id)
            if command:
                commands.append(command)
        return commands

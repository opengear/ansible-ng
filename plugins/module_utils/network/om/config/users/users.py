# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import yaml

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
    remove_empties,
)
from ansible_collections.opengear.om.plugins.module_utils.network.om.facts.facts import Facts

ADMIN_USERNAME = 'root'


class Users(ResourceModule):

    def __init__(self, module):
        super().__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource='users',
        )

    def execute_module(self):
        if self.state in self.ACTION_STATES:
            self._build_user_map()
            if self.state == 'overridden':
                self._state_overridden()
            elif self.state == 'deleted':
                self._state_deleted(self.want if self.want else self.have)
            elif self.state == 'merged':
                self._state_merged()
            elif self.state == 'replaced':
                self._state_replaced()
        elif self.state == 'rendered':
            self._build_user_map()
            self._state_merged()

        self.run_commands()
        result = self.result
        if self._module._diff and result.get('before') and result.get('after'):
            result['diff'] = {
                'before': yaml.dump(result['before'], default_flow_style=False),
                'after': yaml.dump(result['after'], default_flow_style=False),
            }
        return result

    def _build_user_map(self):
        self.user_map = {}
        for user in (self.have or []):
            self.user_map[user['username']] = user

    def _get_existing_user(self, user):
        return self.user_map.get(user.get('username'))

    def _strip_id(self, data):
        d = deepcopy(data)
        d.pop('id', None)
        return d

    def _state_merged(self):
        for user in (self.want or []):
            data = remove_empties(user)
            data.pop('id', None)
            existing = self._get_existing_user(data)
            if existing:
                existing_clean = remove_empties(self._strip_id(existing))
                if 'password' in data:
                    existing_clean.pop('hashed_password', None)
                elif 'hashed_password' in data:
                    existing_clean.pop('password', None)
                merged_data = dict_merge(existing_clean, data)
                if merged_data == existing_clean:
                    continue
                data = merged_data
                self.commands.append({
                    'path': 'users/' + existing['id'],
                    'method': 'PUT',
                    'data': {'user': data},
                })
            else:
                self.commands.append({
                    'path': 'users/',
                    'method': 'POST',
                    'data': {'user': data},
                })

    def _state_replaced(self):
        for user in (self.want or []):
            data = remove_empties(user)
            data.pop('id', None)
            existing = self._get_existing_user(data)
            if existing:
                if data == remove_empties(self._strip_id(existing)):
                    continue
                if 'groups' not in data or data['groups'] is None:
                    data['groups'] = []
                self.commands.append({
                    'path': 'users/' + existing['id'],
                    'method': 'PUT',
                    'data': {'user': data},
                })
            else:
                self.commands.append({
                    'path': 'users/',
                    'method': 'POST',
                    'data': {'user': data},
                })

    def _state_overridden(self):
        deleted_users = deepcopy(self.user_map)
        for user in (self.want or []):
            username = user.get('username')
            if username in deleted_users:
                deleted_users.pop(username)
        self._state_deleted(deleted_users.values())
        self._state_replaced()

    def _state_deleted(self, users):
        for user in (users or []):
            existing = self._get_existing_user(user)
            if existing and existing.get('username') != ADMIN_USERNAME:
                self.commands.append({
                    'path': 'users/' + existing['id'],
                    'method': 'DELETE',
                    'data': None,
                })

    def run_commands(self):
        if self.commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                if hasattr(self._connection, 'send_request'):
                    for cmd in self.commands:
                        self._connection.send_request(cmd['data'], cmd['path'], cmd['method'])
                else:
                    raise NotImplementedError("CLI transport not yet supported for users config")
            self.changed = True

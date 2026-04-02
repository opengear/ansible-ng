# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.opengear.om.plugins.module_utils.network.om.facts.facts import Facts


class Banner(ResourceModule):

    def __init__(self, module):
        super().__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource='banner',
        )

    def execute_module(self):
        if self.state in self.ACTION_STATES:
            if self.state == 'deleted':
                self._state_deleted()
            elif self.state in ('merged', 'replaced', 'overridden'):
                self._state_merged()
        elif self.state == 'rendered':
            self._state_merged()

        self.run_commands()
        return self.result

    def _state_merged(self):
        want_banner = self.want.get('banner', '').strip()
        have_banner = self.have.get('banner', '').strip()
        if want_banner != have_banner:
            self.commands.append({
                'path': 'system/banner',
                'method': 'PUT',
                'data': {'system_banner': {'banner': want_banner}},
            })

    def _state_deleted(self):
        have_banner = self.have.get('banner', '').strip()
        if have_banner:
            self.commands.append({
                'path': 'system/banner',
                'method': 'PUT',
                'data': {'system_banner': {'banner': ''}},
            })

    def run_commands(self):
        if self.commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                if hasattr(self._connection, 'send_request'):
                    for cmd in self.commands:
                        self._connection.send_request(cmd['data'], cmd['path'], cmd['method'])
                else:
                    # TODO: implement CLI transport
                    # self._connection.edit_config(candidate=cli_commands)
                    raise NotImplementedError("CLI transport not yet supported for banner config")
            self.changed = True

# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.users.users import UsersArgs


class UsersFacts(object):

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = UsersArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        if hasattr(connection, 'send_request'):
            return connection.send_request(None, 'users')['users']
        else:
            raise NotImplementedError("CLI transport not yet supported for users facts")

    def populate_facts(self, connection, ansible_facts, data=None):
        if not data:
            data = self.get_device_data(connection)

        objs = []
        for instance in data:
            if instance:
                obj = self.render_config(self.generated_spec, instance)
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('users', None)
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            ansible_facts['ansible_network_resources']['users'] = params['config']
        else:
            ansible_facts['ansible_network_resources']['users'] = []

        return ansible_facts

    def render_config(self, spec, conf):
        config = deepcopy(spec)
        for option in config.keys():
            if option in conf:
                config[option] = conf[option]
        return utils.remove_empties(config)

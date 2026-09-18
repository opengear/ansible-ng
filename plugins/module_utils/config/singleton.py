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
    reconcile_full_replace_lists,
    remove_empties,
    to_list,
)


class SingletonConfigBase(ConfigBase):
    """
    Base class for Opengear *singleton* system resources - attributes of which
    exactly one instance exists on the device (banner, hostname, timezone,
    cell reliability test, ...).

    Unlike collection resources (groups, users), singletons have no ids and no
    meaningful ``deleted``/``overridden`` semantics, so only ``merged``,
    ``replaced``, ``gathered`` and ``rendered`` are supported. ``merged`` and
    ``replaced`` behave identically for a singleton: each provided field that
    differs from the device is pushed with a single ``PUT``.

    Subclasses declare:
      * ``resource_name`` - the ansible_network_resources key / facts subset.
      * ``field_map`` - ``{config_field: (endpoint, [body_path...])}`` mapping
        each top-level ``config`` field to its REST endpoint and the sequence
        of keys the value must be wrapped in to form the request body.
    """

    resource_name = None
    field_map = {}
    # {field: {sub_key: identity_key}} - for each top-level field whose
    # endpoint PUT replaces whole nested lists, the list-valued sub_keys and
    # what identifies an item. On merged, items are matched against the
    # device's current list by identity_key and merged/appended in place;
    # on replaced, want's list is used as-is.
    full_replace_list_fields = {}

    ACTION_STATES = ['merged', 'replaced']

    gather_subset = [
        '!all',
        '!min',
    ]

    def __init__(self, module):
        super(SingletonConfigBase, self).__init__(module)
        self._diff_after = {}

    def get_resource_facts(self):
        """ Get the 'facts' (the current configuration) for this resource.

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, [self.resource_name])
        resource_facts = facts['ansible_network_resources'].get(self.resource_name)
        if not resource_facts:
            return {}
        return resource_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES:
            existing_facts = self.get_resource_facts()
        else:
            existing_facts = {}
        if self.state in self.ACTION_STATES or self.state == 'rendered':
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
        if self.state in self.ACTION_STATES:
            result['commands'] = commands
        if self.state in self.ACTION_STATES or self.state == 'gathered':
            if result['changed'] and self._module.check_mode:
                # Simulated diff: nothing is sent in check mode so the
                # expected changes are displayed in diff
                changed_facts = self._diff_after
            else:
                changed_facts = self.get_resource_facts()
        elif self.state == 'rendered':
            result['rendered'] = commands
        if self.state in self.ACTION_STATES:
            result['before'] = existing_facts
            if result['changed']:
                result['after'] = changed_facts
                if self._module._diff:
                    result['diff'] = {
                        'before': json.dumps(existing_facts, indent=4) + '\n',
                        'after': json.dumps(changed_facts, indent=4) + '\n',
                    }
        elif self.state == 'gathered':
            result['gathered'] = changed_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_facts):
        """ Collect the desired configuration from module params and diff it
            against the current configuration.

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        # Drop unset params so AnsibleModule's None-filled (sub)options are not
        # pushed to the device and mistaken for a request to clear them.
        want = remove_empties(self._module.params['config'] or {})
        have = existing_facts
        return to_list(self._generate_commands(want, have))

    def _generate_commands(self, want, have):
        """ Build a PUT command for each provided field that differs from the
            device. Identical for ``merged`` and ``replaced`` on a singleton.

            The modified field(s) are combined with the device's current values
            before sending, as some singleton endpoints (e.g. session_timeout)
            reject a request that omits any of their fields.

        :rtype: A list
        :returns: the commands necessary to reach the desired configuration
        """
        commands = []
        self._diff_after = deepcopy(have)
        to_set = dict_diff(have, want)
        for field in to_set:
            endpoint, body_path = self.field_map[field]
            data = want[field]
            if isinstance(data, dict) and isinstance(have.get(field), dict):
                identity_keys = self.full_replace_list_fields.get(field, {})
                if self.state == 'merged' and identity_keys:
                    data = reconcile_full_replace_lists(have[field], data, identity_keys)
                data = dict_merge(have[field], data, identity_keys)
                # The device retains its own id across a PUT; never echo it
                # back in the request, but keep it in the simulated facts.
                self._diff_after[field] = deepcopy(data)
                data.pop('id', None)
            else:
                self._diff_after[field] = data
            for key in reversed(body_path):
                data = {key: data}
            commands.append(command_builder(data, endpoint, method='PUT'))
        return commands

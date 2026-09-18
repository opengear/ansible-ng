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

AUTHORIZED_KEYS_PATH = 'system/system_authorized_keys'


class SystemAuthorizedKeys(ConfigBase):
    """
    Manages system-level SSH authorized keys on Opengear devices.

    Unlike users_authorized_keys (scoped under a user), these are a flat
    system-wide collection; each record carries the associated ``username`` and
    the ``key`` string, and the device assigns an ``id`` used for deletion.
    A record's identity for idempotency is the ``(username, key)`` pair.
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'system_authorized_keys',
    ]

    def __init__(self, module):
        super(SystemAuthorizedKeys, self).__init__(module)

    def get_system_authorized_keys_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A list
        :returns: The current configuration as a list
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        facts_data = facts['ansible_network_resources'].get('system_authorized_keys')
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
            existing_facts = self.get_system_authorized_keys_facts()
        else:
            existing_facts = []
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

        result['commands'] = commands

        if self.state in self.ACTION_STATES:
            if result['changed'] and self._module.check_mode:
                # Simulated diff: nothing is sent in check mode so the
                # expected changes are displayed in diff
                changed_facts = self._simulate_after(existing_facts, commands)
            else:
                changed_facts = self.get_system_authorized_keys_facts()
            result['before'] = existing_facts
            if result['changed']:
                result['after'] = changed_facts
                if self._module._diff:
                    result['diff'] = {
                        'before': json.dumps(existing_facts, indent=4) + '\n',
                        'after': json.dumps(changed_facts, indent=4) + '\n',
                    }
        elif self.state == 'gathered':
            result['gathered'] = existing_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a list from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config'] or []
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
        # Map each existing record's (username, key) identity to its device id.
        have_ids = {(entry['username'], entry['key']): entry['id'] for entry in have}

        state = self._module.params['state']
        if state == 'deleted':
            commands = self._state_deleted(want, have_ids)
        elif state == 'replaced':
            commands = self._state_replaced(want, have_ids)
        else:
            commands = self._state_merged(want, have_ids)
        return commands

    @staticmethod
    def _simulate_after(existing_facts, commands):
        """ Simulate the expected after-state by the given commands applied to
            the existing facts. """
        after = deepcopy(existing_facts)
        for command in commands:
            if command['method'] == 'POST':
                after.append(command['data']['system_authorized_key'])
            elif command['method'] == 'DELETE':
                key_id = command['path'].rstrip('/').split('/')[-1]
                after = [entry for entry in after if entry.get('id') != key_id]
        return after

    @staticmethod
    def _post(entry):
        """ Build a POST command that adds a single authorized key. """
        data = {'username': entry['username'], 'key': entry['key']}
        if entry.get('multi_field_identifier'):
            data['multi_field_identifier'] = entry['multi_field_identifier']
        return {
            'path': AUTHORIZED_KEYS_PATH,
            'data': {'system_authorized_key': data},
            'method': 'POST',
        }

    @staticmethod
    def _delete(key_id):
        """ Build a DELETE command for a single authorized key by device id. """
        return {
            'path': '{0}/{1}'.format(AUTHORIZED_KEYS_PATH, key_id),
            'data': None,
            'method': 'DELETE',
        }

    @staticmethod
    def _state_merged(want, have_ids):
        """ Add keys not already present. Existing keys are preserved. """
        commands = []
        for entry in want:
            if (entry['username'], entry['key']) not in have_ids:
                commands.append(SystemAuthorizedKeys._post(entry))
        return commands

    @staticmethod
    def _state_deleted(want, have_ids):
        """ Remove the specified keys where present (idempotent otherwise). """
        commands = []
        for entry in want:
            key_id = have_ids.get((entry['username'], entry['key']))
            if key_id:
                commands.append(SystemAuthorizedKeys._delete(key_id))
        return commands

    @staticmethod
    def _state_replaced(want, have_ids):
        """ Converge the collection to exactly the provided keys: delete keys
            not in want, add keys not already present.
        """
        commands = []
        want_identities = {(entry['username'], entry['key']) for entry in want}

        for identity, key_id in have_ids.items():
            if identity not in want_identities:
                commands.append(SystemAuthorizedKeys._delete(key_id))

        for entry in want:
            if (entry['username'], entry['key']) not in have_ids:
                commands.append(SystemAuthorizedKeys._post(entry))
        return commands

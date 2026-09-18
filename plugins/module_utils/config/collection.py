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
    dict_diff,
    dict_merge,
    remove_empties,
    to_list,
)


class CollectionConfigBase(ConfigBase):
    """
    Base class for Opengear *collection* resources - id-keyed lists of
    records that support full add/update/remove semantics via POST/PUT/DELETE.

    Subclasses declare:
      * ``resource_name`` - the ansible_network_resources key / facts subset.
      * ``endpoint`` - the collection's REST path, e.g. ``services/syslog``.
      * ``item_key`` - the JSON body key each item is wrapped in for
        POST/PUT/GET-by-id requests, e.g. ``syslogServer``.
      * ``identity_fields`` - the tuple of config fields that make up a
        record's business identity (used to match ``want`` entries against
        ``have`` when no ``id`` is provided), e.g. ``('address', 'port',
        'protocol')`` or ``('name',)``.
    """

    resource_name = None
    endpoint = None
    item_key = None
    identity_fields = ()
    # Device-assigned fields returned in facts but not accepted in a
    # POST/PUT body.
    readonly_fields = ('id', 'multi_field_identifier')

    gather_subset = [
        '!all',
        '!min',
    ]

    def __init__(self, module):
        super(CollectionConfigBase, self).__init__(module)
        self._diff_after = []

    def get_resource_facts(self):
        """ Get the 'facts' (the current configuration) for this resource.

        :rtype: A list
        :returns: The current configuration as a list
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, [self.resource_name])
        resource_facts = facts['ansible_network_resources'].get(self.resource_name)
        if not resource_facts:
            return []
        return resource_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        if self.state in self.ACTION_STATES or self.state == 'gathered':
            existing_facts = self.get_resource_facts()
        else:
            existing_facts = []
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
        elif self.state == 'rendered':
            result['rendered'] = commands
        else:
            result['commands'] = []
        if self.state in self.ACTION_STATES:
            if result['changed'] and self._module.check_mode:
                # Simulated diff: nothing is sent in check mode so the
                # expected changes are displayed in diff
                changed_facts = self._diff_after
            else:
                changed_facts = self.get_resource_facts()
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
        """ Collect the desired configuration from module params and diff it
            against the current configuration.

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = [remove_empties(entry) for entry in (self._module.params['config'] or [])]
        have = existing_facts
        self._diff_after = deepcopy(have)
        return to_list(self.set_state(want, have))

    def _identity(self, entry):
        """ The business identity tuple for a record, used to match ``want``
            entries against ``have`` when the record has no known id. """
        return tuple(entry.get(field) for field in self.identity_fields)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a list
        :param have: the current configuration as a list
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        have_by_identity = {self._identity(entry): entry for entry in have}

        state = self._module.params['state']
        if state == 'deleted':
            commands = self._state_deleted(want, have_by_identity)
        elif state == 'replaced':
            commands = self._state_replaced(want, have_by_identity)
        elif state == 'overridden':
            commands = self._state_overridden(want, have_by_identity)
        else:
            commands = self._state_merged(want, have_by_identity)
        return commands

    def _post(self, entry):
        return {
            'path': self.endpoint,
            'data': {self.item_key: entry},
            'method': 'POST',
        }

    def _put(self, entry_id, entry):
        return {
            'path': '{0}/{1}'.format(self.endpoint, entry_id),
            'data': {self.item_key: entry},
            'method': 'PUT',
        }

    def _delete(self, entry_id):
        self._diff_after = [item for item in self._diff_after if item.get('id') != entry_id]
        return {
            'path': '{0}/{1}'.format(self.endpoint, entry_id),
            'data': None,
            'method': 'DELETE',
        }

    def _upsert(self, entry, have_by_identity):
        """ Build a POST for a new record, or a PUT if it differs from the
            existing record with the same identity. The PUT body is the
            existing record with the provided fields merged in, since these
            endpoints expect the complete record on every PUT. Returns None
            if the record is unchanged. """
        existing = have_by_identity.get(self._identity(entry))
        if existing is None:
            self._diff_after.append(entry)
            return self._post(entry)
        existing_fields = {k: v for k, v in existing.items() if k not in self.readonly_fields}
        merged = dict_merge(existing_fields, entry)
        if dict_diff(existing_fields, merged):
            after_entry = dict(existing)
            after_entry.update(merged)
            for index, item in enumerate(self._diff_after):
                if item.get('id') == existing['id']:
                    self._diff_after[index] = after_entry
                    break
            return self._put(existing['id'], merged)
        return None

    def _state_merged(self, want, have_by_identity):
        """ Add new records, update changed ones. Untouched records are left
            as-is. """
        commands = []
        for entry in want:
            command = self._upsert(entry, have_by_identity)
            if command:
                commands.append(command)
        return commands

    def _state_replaced(self, want, have_by_identity):
        """ Identical to merged for this resource kind: every provided
            record is added or updated in place; nothing is removed. """
        return self._state_merged(want, have_by_identity)

    def _state_overridden(self, want, have_by_identity):
        """ Converge the collection to exactly the provided records: delete
            records not in want, add/update the rest. """
        commands = []
        want_identities = {self._identity(entry) for entry in want}
        for identity, existing in have_by_identity.items():
            if identity not in want_identities:
                commands.append(self._delete(existing['id']))
        commands.extend(self._state_merged(want, have_by_identity))
        return commands

    def _state_deleted(self, want, have_by_identity):
        """ Remove the specified records where present (idempotent
            otherwise). """
        commands = []
        for entry in want:
            existing = have_by_identity.get(self._identity(entry))
            if existing:
                commands.append(self._delete(existing['id']))
        return commands

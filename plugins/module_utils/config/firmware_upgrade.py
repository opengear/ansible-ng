# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import json

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.config.base import ConfigBase
from ansible_collections.opengear.ng.plugins.module_utils.facts.facts import Facts
from ansible_collections.opengear.ng.plugins.module_utils.utils.utils import (
    command_builder,
    to_list,
)


class FirmwareUpgrade(ConfigBase):
    """
    Manages firmware upgrade for Opengear devices.
    """

    gather_subset = ['!all', '!min']
    gather_network_resources = ['firmware_upgrade']

    def __init__(self, module):
        super(FirmwareUpgrade, self).__init__(module)

    def get_firmware_upgrade_facts(self):
        """Get the current firmware version and upgrade status.

        :rtype: dict
        :returns: The current firmware facts
        """
        facts, _warnings = Facts(self._module).get_facts(
            self.gather_subset, self.gather_network_resources
        )
        return facts['ansible_network_resources'].get('firmware_upgrade', {})

    def execute_module(self):
        """Execute the module.

        :rtype: dict
        :returns: The result from module execution
        """
        result = {'changed': False}
        warnings = list()
        commands = list()

        if self.state == 'gathered':
            result['gathered'] = self.get_firmware_upgrade_facts()
            result['warnings'] = warnings
            return result

        existing_facts = self.get_firmware_upgrade_facts()
        commands.extend(self.set_config(existing_facts, warnings))

        # idempotent if desired version == current version
        if not commands and self.state == 'merged':
            want = self._module.params['config']
            self._module.warn(
                f"Version {want.get('version')} already installed. No upgrade required."
            )

        if commands and self.state in self.ACTION_STATES:
            if not self._module.check_mode:
                for command in commands:
                    try:
                        if command['method'] == 'POST_MULTIPART':
                            # merged - upgrade image
                            file_path = command['data'].get('firmware_file')
                            additional_fields = {}
                            if command['data'].get('firmware_url'):
                                additional_fields['firmware_url'] = command['data']['firmware_url']
                            if command['data'].get('firmware_options'):
                                additional_fields['firmware_options'] = command['data']['firmware_options']
                            response = self._connection.send_multipart_request(
                                command['path'],
                                file_path=file_path,
                                additional_fields=additional_fields,
                            )
                        else:
                            # gathered - get status
                            self._connection.send_request(
                                command['data'], command['path'], command['method']
                            )
                    except ConnectionError as exc:
                        self._module.warn(f"Firmware upgrade error: {exc}")
                        raise exc
            result['changed'] = True
            if self._module._diff:
                want = self._module.params['config']
                result['diff'] = {
                    'before': json.dumps({'current_version': existing_facts.get('current_version')}, indent=4) + '\n',
                    'after': json.dumps({'current_version': want.get('version')}, indent=4) + '\n',
                }

        result['commands'] = commands

        if self.state in self.ACTION_STATES:
            result['before'] = existing_facts
            if result['changed']:
                result['after'] = self.get_firmware_upgrade_facts()

        result['warnings'] = warnings
        return result

    def set_config(self, existing_facts, warnings):
        """Collect the configuration from the args passed to the module.

        :rtype: list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_facts
        resp = self.set_state(want, have, warnings)
        return to_list(resp)

    def set_state(self, want, have, warnings):
        """Select the appropriate function based on the state provided.

        :param want: the desired configuration as a dict
        :param have: the current configuration as a dict
        :rtype: list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        state = self._module.params['state']
        if state == 'merged':
            return self._state_merged(want, have)
        return []

    @staticmethod
    def _state_merged(want, have):
        """The command generator when state is merged.

        :rtype: list
        :returns: the commands necessary to initiate a firmware upgrade
                  if the current version differs from the desired version
        """
        if not want:
            return []

        if not want.get('firmware_image'):
            raise ValueError("firmware_image is required for state: merged")

        current_version = have.get('current_version')
        desired_version = want.get('version')

        # Idempotent - already at desired version
        if desired_version and current_version == desired_version:
            return []

        firmware_image = want['firmware_image']
        is_url = firmware_image.startswith('http://') or firmware_image.startswith('https://')

        # Include firmware options
        options = []
        if want.get('ignore_version'):
            options.append('-I')
        if want.get('erase_config'):
            options.append('-E')
        firmware_options = ' '.join(options) if options else None

        # Build multipart request - include file or URL
        if is_url:
            return [command_builder(
                {
                    'firmware_url': firmware_image,
                    'firmware_options': firmware_options,
                },
                'system/firmware_upgrade',
                method='POST_MULTIPART'
            )]
        else:
            return [command_builder(
                {
                    'firmware_file': firmware_image,
                    'firmware_options': firmware_options,
                },
                'system/firmware_upgrade',
                method='POST_MULTIPART'
            )]

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'opengear'
}

DOCUMENTATION = """
---
module: system
version_added: '1.0.0'
short_description: Manages configuration of system attributes on Opengear devices
description:
  - Manages configuration of system attributes on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of system attributes on Opengear devices
    type: dict
    suboptions:
      admin_info:
        type: dict
        description: Update the Operations Manager appliance system information
        suboptions:
          hostname:
            type: str
            description: hostname or address
          contact:
            type: str
            description: contact info
          location:
            type: str
            description: location
      banner:
        type: str
        description: Update the Operations Manager appliance banner text.
      hostname:
        type: str
        description: hostname or address
      webui_session_timeout:
        type: int
        description: Update the WebUI session timeout (in minutes).
      cli_session_timeout:
        type: int
        description: Update the CLI session timeout (in minutes)
      system_authorized_keys:
        description: Add an SSH key for the specified user
        type: list
        elements: dict
        suboptions:
          id:
            type: str
            description: The SSH key id
          multi_field_identifier:
            type: str
            description: Unique identifier for this authorized keys record.
          key:
            type: str
            description: The SSH key
          username:
            type: str
            description: The user associated with the SSH key
      ssh_port:
        type: int
        description: Update the system SSH port
      timezone:
        type: str
        description: Update the system timezone
      time:
        type: str
        description: Update the Operations Manager current time
      cell_reliability_test:
        type: dict
        description: Update configuration items related to running the cell reliability test.
        suboptions:
          enabled:
            type: bool
            description: enabled or disabled
          period:
            type: int
            description: period
          test_url:
            type: list
            elements: str
            description: test url
          signal_strength_threshold:
            type: dict
            description: signal threshold
            suboptions:
              lower:
                type: int
                description: lower threshold
              upper:
                type: int
                description: upper threshold
      reboot:
        type: bool
        description: reboot
  state:
    description:
    - The state of the configuration after module completion.
    type: str
    choices:
    - merged
    - overridden
    - deleted
    - gathered
    - rendered
    default: merged
"""

EXAMPLES = """
- name: Configure system information
  opengear.ng.system:
    config:
      hostname: om-device-01
      timezone: Australia/Brisbane
      banner: "Authorized access only"
      ssh_port: 22
      webui_session_timeout: 30
      cli_session_timeout: 30
    state: merged

- name: Configure admin info
  opengear.ng.system:
    config:
      admin_info:
        hostname: om-device-01
        contact: netops@example.com
        location: Server Room A, Rack 3
    state: merged

- name: Add SSH authorized key
  opengear.ng.system:
    config:
      system_authorized_keys:
        - username: admin
          key: "{{ ssh_public_key }}"
    state: merged

- name: Configure cell reliability test
  opengear.ng.system:
    config:
      cell_reliability_test:
        enabled: true
        period: 300
        test_url:
          - https://example.com
        signal_strength_threshold:
          lower: -110
          upper: -70
    state: merged

- name: Gather system facts
  opengear.ng.facts:
    gather_network_resources:
      - system
"""

RETURN = """
before:
  description: The configuration before the module is executed.
  returned: always
  type: dict
after:
  description: The configuration after the module is executed.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system import SystemArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system import System


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemArgs.argument_spec,
                           supports_check_mode=True)

    result = System(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

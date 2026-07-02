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
module: user_authorized_keys
version_added: '1.0.0'
short_description: Manages configuration of user authorized keys on Opengear devices
description:
  - Manages configuration of user SSH authorized keys on Opengear devices
  - Authorized keys are scoped to a specific user, identified by username.
  - The user must already exist before managing their authorized keys.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of user authorized keys on Opengear devices
    type: list
    elements: dict
    suboptions:
      username:
        type: str
        description: The username of the user whose authorized keys are being managed.
        required: true
      keys:
        type: list
        elements: str
        description: List of SSH public key strings to manage for this user.
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    choices:
      - merged
      - replaced
      - deleted
      - gathered
    default: merged
notes:
  - Diff output shows the expected configuration change based on the commands
    generated. It does not reflect the actual device state after execution,
    which may differ due to device-side normalization or concurrent changes.
    Use state=gathered after a run to verify the actual device state.
  - Offline rendering of commands is not supported as resolving usernames to
    user ids requires device connection.
"""

EXAMPLES = """
- name: Add authorized keys for a user
  opengear.ng.user_authorized_keys:
    config:
      - username: netops
        keys:
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... netops@laptop"
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp... netops@workstation"
    state: merged

- name: Replace all authorized keys for a user
  opengear.ng.user_authorized_keys:
    config:
      - username: netops
        keys:
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... netops@laptop"
    state: replaced

- name: Delete specific authorized keys for a user
  opengear.ng.user_authorized_keys:
    config:
      - username: netops
        keys:
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... netops@laptop"
    state: deleted

- name: Gather authorized keys facts
  opengear.ng.facts:
    gather_network_resources:
      - user_authorized_keys
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.user_authorized_keys import UserAuthorizedKeysArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.user_authorized_keys import UserAuthorizedKeys


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=UserAuthorizedKeysArgs.argument_spec,
                           supports_check_mode=True)

    result = UserAuthorizedKeys(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

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
module: users
version_added: '1.0.0'
short_description: Manages configuration of users on Opengear devices
description:
  - Manages configuration of users on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of users on Opengear devices
    type: list
    elements: dict
    suboptions:
      description:
        type: str
        description: A descriptive string for the user.
      id:
        type: str
        description: Unique identifier for the user. (read-only)
      username:
        type: str
        description: The POSIX name for the user.
      enabled:
        type: bool
        description: Whether the user is enabled. Only enabled users may log in.
      password:
        type: str
        description: |
          The plaintext password to set for the user.
          For increased security, it is strongly recommended to enable Password Complexity.
      hashed_password:
        type: str
        description: A hashed password to set for the user, compatible with the crypt GNU C Library function.
      no_password:
        type: bool
        description: |
          Remote authentication used if this flag is set.
          Set this to true for remote-only (AAA) users. Both password and hashed_password must be unset.
          Set this to false for local users. One of password or hashed_password is required.
      ssh_password_enabled:
        type: bool
        description: |
          Whether SSH password access is enabled. (Default: true)
          If false a user can only use SSH with user_authorized_keys configured.
      groups:
        type: list
        elements: str
        description: A list of groups for which this user is a member.
      groupNames:
        type: list
        elements: str
        description: A duplicate list of group names for the user. (read-only)
  state:
    description:
    - The state of the configuration after module completion.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - gathered
    - rendered
    default: merged
notes:
  - Diff output shows the expected configuration change based on the commands
    generated. It does not reflect the actual device state after execution,
    which may differ due to device-side normalization or concurrent changes.
    Use state=gathered after a run to verify the actual device state.
"""

EXAMPLES = """
- name: Configure users
  opengear.ng.users:
    config:
      - username: netops
        description: Network operations user
        enabled: true
        password: "{{ user_password }}"
        no_password: false
        ssh_password_enabled: true
        groups:
          - netops
      - username: readonly
        description: Read only user
        enabled: true
        password: "{{ user_password }}"
        no_password: false
        ssh_password_enabled: false
        groups:
          - readonly
    state: merged

- name: Delete a user
  opengear.ng.users:
    config:
      - username: readonly
    state: deleted

- name: Gather user facts
  opengear.ng.facts:
    gather_network_resources:
      - users
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.users import UsersArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.users import Users


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=UsersArgs.argument_spec,
                           supports_check_mode=True)

    result = Users(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'opengear',
}

DOCUMENTATION = """
---
module: om_users
version_added: 1.0.0
short_description: Manages user attributes of opengear om users
description:
  - Manages user attributes of opengear om users
author:
  - "Adrian Van Katwyk (@avankatwyk)"
options:
  config:
    description: Retrieve and update user information
    type: list
    elements: dict
    suboptions:
      description:
        type: str
        description: suboption description
      id:
        type: str
        description: id
      username:
        type: str
        description: username
      enabled:
        type: bool
        description: user enabled or not
      password:
        type: str
        description: Clear text password
      hashed_password:
        type: str
        description: A hashed password compatible with the crypt GNU C Library function.
      no_password:
        type: bool
        description: Remote authentication used if this flag is set.
      ssh_password_enabled:
        type: bool
        description: Whether SSH password access is enabled (default is true). If false a user can only use SSH with SSH keys.
        default: yes
      groups:
        type: list
        elements: str
        description: user groups
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
"""

EXAMPLES = """
- name: Create a new user
  opengear.om.om_users:
    config:
      - username: testuser
        password: secret123
        enabled: true
        groups:
          - admin
    state: merged

- name: Delete a user
  opengear.om.om_users:
    config:
      - username: testuser
    state: deleted

- name: Gather current users
  opengear.om.om_users:
    state: gathered
"""

RETURN = """
before:
  description: The configuration before the module invocation.
  returned: always
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.users.users import UsersArgs
from ansible_collections.opengear.om.plugins.module_utils.network.om.config.users.users import Users


def main():
    module = AnsibleModule(
        argument_spec=UsersArgs.argument_spec,
        supports_check_mode=True,
    )
    result = Users(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

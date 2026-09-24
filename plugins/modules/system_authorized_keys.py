#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: system_authorized_keys
version_added: '0.1.0'
short_description: Manages system-level SSH authorized keys on Opengear devices
description:
  - Manages system-level SSH authorized keys on Opengear devices.
  - These are a flat, system-wide collection of keys, each associated with a
    username. This is distinct from M(opengear.ng.users_authorized_keys), which
    manages keys scoped to an individual user account.
  - A key's identity for idempotency is the combination of its C(username) and
    C(key) string.
author:
  - Opengear (@opengear)
options:
  config:
    description: The system authorized keys to manage.
    type: list
    elements: dict
    suboptions:
      username:
        type: str
        description: The user associated with the SSH key.
        required: true
      key:
        type: str
        description: The SSH public key string.
        required: true
      multi_field_identifier:
        type: str
        description: Optional unique identifier for this authorized key record.
  state:
    description:
      - The state of the configuration after module completion.
      - C(merged) adds the provided keys, C(deleted) removes them, and
        C(replaced) converges the collection to exactly the provided keys.
    type: str
    choices:
      - merged
      - replaced
      - deleted
      - gathered
    default: merged
"""

EXAMPLES = """
- name: Add system authorized keys
  opengear.ng.system_authorized_keys:
    config:
      - username: root
        key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... root@laptop"
      - username: admin
        key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp... admin@workstation"
    state: merged

- name: Replace all system authorized keys for the listed identities
  opengear.ng.system_authorized_keys:
    config:
      - username: root
        key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... root@laptop"
    state: replaced

- name: Delete a system authorized key
  opengear.ng.system_authorized_keys:
    config:
      - username: admin
        key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp... admin@workstation"
    state: deleted

- name: Gather system authorized keys facts
  opengear.ng.facts:
    gather_network_resources:
      - system_authorized_keys
"""

RETURN = """
before:
  description: The configuration before the module is executed.
  returned: always
  type: list
after:
  description: The configuration after the module is executed.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_authorized_keys import SystemAuthorizedKeysArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system_authorized_keys import SystemAuthorizedKeys


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemAuthorizedKeysArgs.argument_spec,
                           supports_check_mode=True)

    result = SystemAuthorizedKeys(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

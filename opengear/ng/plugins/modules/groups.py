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
module: groups
version_added: '1.0.0'
short_description: Manages configuration of groups on Opengear devices
description:
  - Manages configuration of groups on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of groups on Opengear devices
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description: group id
      groupname:
        type: str
        description: group name
      description:
        type: str
        description: A description of the group's purpose.
      enabled:
        type: bool
        description: group enabled or disabled
      access_rights:
        type: list
        elements: str
        description: List of access rights assigned to the group.
      members:
        type: list
        elements: str
        description: List of user ids or usernames that are members of the group.
      ports:
        type: list
        description: List of port ids assigned to the group.
        elements: str
      mode:
        type: str
        description: Group mode. Deprecated since 2022/08, use C(access_rights) instead.
      role:
        type: str
        description: Group role. Deprecated since 2022/08, use C(access_rights) instead.
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
- name: Configure groups
  opengear.ng.groups:
    config:
      - groupname: netops
        description: Network operations group
        enabled: true
        access_rights:
          - admin
      - groupname: readonly
        description: Read only group
        enabled: true
        access_rights:
          - web_ui
          - pmshell
        ports:
          - ports-1
          - ports-2
    state: merged

- name: Delete a group
  opengear.ng.groups:
    config:
      - groupname: readonly
    state: deleted

- name: Gather group facts
  opengear.ng.facts:
    gather_network_resources:
      - groups
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.groups import GroupsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.groups import Groups


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=GroupsArgs.argument_spec,
                           supports_check_mode=True)

    result = Groups(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'opengear'
}

DOCUMENTATION = """
---
module: om_user_authorized_keys
version_added: '1.0.0'
short_description: Manages SSH authorized keys for opengear om users
description:
  - Manages SSH authorized keys for opengear om users.
  - Authorized keys are scoped to a specific user, identified by username.
  - The user must already exist before managing their authorized keys.
author:
  - Opengear (@opengear)
options:
  config:
    description: List of users and their authorized keys to manage.
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
      - merged - adds any keys not already present, existing keys are preserved.
      - replaced - replaces all keys for the user with only those specified.
      - deleted - removes the specified keys from the user.
      - gathered - returns the current authorized keys as structured data.
    type: str
    choices:
      - merged
      - replaced
      - deleted
      - gathered
    default: merged
"""

EXAMPLES = """
- name: Add authorized keys for a user
  opengear.om.om_user_authorized_keys:
    config:
      - username: netops
        keys:
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... netops@laptop"
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDcsp... netops@workstation"
    state: merged

- name: Replace all authorized keys for a user
  opengear.om.om_user_authorized_keys:
    config:
      - username: netops
        keys:
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... netops@laptop"
    state: replaced

- name: Delete specific authorized keys for a user
  opengear.om.om_user_authorized_keys:
    config:
      - username: netops
        keys:
          - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTRO6c... netops@laptop"
    state: deleted

- name: Gather authorized keys facts
  opengear.om.om_facts:
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
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.user_authorized_keys.user_authorized_keys import UserAuthorizedKeysArgs
from ansible_collections.opengear.om.plugins.module_utils.network.om.config.user_authorized_keys.user_authorized_keys import UserAuthorizedKeys


def main():
    """
    Main entry point for module execution
 
    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=UserAuthorizedKeysArgs.argument_spec,
                           supports_check_mode=True)
 
    result = UserAuthorizedKeys(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

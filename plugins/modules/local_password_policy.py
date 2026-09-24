#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: local_password_policy
version_added: '0.1.0'
short_description: Manages the local password policy on Opengear devices
description:
  - Manages the expiry and complexity policy applied to local user passwords
    on Opengear devices.
  - The local password policy resource is a singleton — only one policy exists
    on the device.
  - The device requires every field on each request, so C(merged), C(replaced),
    and C(overridden) all behave identically here, merging your specified
    fields onto the device's current policy before sending.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage the local password policy on Opengear devices
    type: dict
    suboptions:
      password_expiry_interval_enabled:
        description: Enable password expiry after I(password_expiry_interval_days).
        type: bool
      password_expiry_interval_days:
        description:
          - The number of days after which a password should expire.
          - Only applies when I(password_expiry_interval_enabled) is C(true).
        type: int
      password_complexity_enabled:
        description:
          - Enable password complexity enforcement.
          - This also requires that a new password is not identical to the
            previous password. Applies to all local users, including root.
        type: bool
      password_minimum_length:
        description:
          - The minimum required length for passwords. Cannot be set below C(6).
          - Only applies when I(password_complexity_enabled) is C(true).
        type: int
      password_must_contain_upper_case:
        description:
          - Require at least one uppercase character (A-Z) in passwords.
          - Only applies when I(password_complexity_enabled) is C(true).
        type: bool
      password_must_contain_special:
        description:
          - Require at least one special character (anything other than A-Z
            or 0-9) in passwords.
          - Only applies when I(password_complexity_enabled) is C(true).
        type: bool
      password_must_contain_number:
        description:
          - Require at least one numeric character (0-9) in passwords.
          - Only applies when I(password_complexity_enabled) is C(true).
        type: bool
      password_disallow_username:
        description:
          - Reject passwords that contain the account's username (in some
            form). Not enforced for usernames shorter than 3 characters.
          - Only applies when I(password_complexity_enabled) is C(true).
        type: bool
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - gathered
      - rendered
    default: merged
"""

EXAMPLES = """
- name: Enforce password complexity with a 10 character minimum
  opengear.ng.local_password_policy:
    config:
      password_complexity_enabled: true
      password_minimum_length: 10
      password_must_contain_upper_case: true
      password_must_contain_number: true
      password_must_contain_special: true
      password_disallow_username: true
    state: merged

- name: Enable 90 day password expiry
  opengear.ng.local_password_policy:
    config:
      password_expiry_interval_enabled: true
      password_expiry_interval_days: 90
    state: replaced

- name: Disable password complexity enforcement
  opengear.ng.local_password_policy:
    config:
      password_complexity_enabled: false
    state: merged

- name: Gather the current local password policy
  opengear.ng.local_password_policy:
    state: gathered

- name: Gather local password policy facts via facts module
  opengear.ng.facts:
    gather_network_resources:
      - local_password_policy
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.local_password_policy import LocalPasswordPolicyArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.local_password_policy import LocalPasswordPolicy


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=LocalPasswordPolicyArgs.argument_spec,
                           supports_check_mode=True)

    result = LocalPasswordPolicy(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

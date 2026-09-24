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
module: system_time
version_added: '0.1.0'
short_description: Manages the system clock and timezone on Opengear devices
description:
  - Manages the system clock and timezone on Opengear devices.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage the system clock and timezone on Opengear devices
    type: dict
    suboptions:
      time:
        type: str
        description:
        - Update the system time as a formatted string.
        - "Supported formats: C(HH:MM mmm DD, YYYY) eg. C(14:30 Mar 24, 2022) for 2:30pm 24th March 2022"
        - "Or: C(HH:MM DD mmm YYYY) eg. C(14:30 24 Mar 2022) for 2:30pm 24th March 2022"
        - This setting is not idempotent; when provided the module always reports
          a change because the device clock advances between fact gathering and
          comparison. It is only pushed when explicitly provided.
        - By default the current time is not returned by fact gathering and never
          appears in C(before)/C(after) diffs. Set O(gather_time=true) with
          O(state=gathered) to read it.
      timezone:
        type: str
        description: Update the system timezone. This setting is idempotent.
  gather_time:
    description:
    - When C(true) and O(state=gathered), include the current device time in the
      gathered facts. Has no effect in other states, so the momentary clock value
      can never leak into a C(before)/C(after) diff.
    type: bool
    default: false
  state:
    description:
    - The state of the configuration after module completion.
    - C(merged) and C(replaced) both update only the settings provided; unspecified
      settings are left untouched (this resource has no items to remove).
    type: str
    choices:
    - merged
    - replaced
    - gathered
    - rendered
    default: merged
"""

EXAMPLES = """
- name: Set the system timezone
  opengear.ng.system_time:
    config:
      timezone: Australia/Brisbane
    state: merged

- name: Set the system clock
  opengear.ng.system_time:
    config:
      time: "13:58 Jul 13, 2026"
    state: merged

- name: Gather the timezone (the clock is excluded by default)
  opengear.ng.facts:
    gather_network_resources:
      - system_time

- name: Gather timezone and the current device clock
  opengear.ng.system_time:
    state: gathered
    gather_time: true
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_time import SystemTimeArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system_time import SystemTime


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemTimeArgs.argument_spec,
                           supports_check_mode=True)

    result = SystemTime(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

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
module: system_firmware_upgrade
version_added: '0.1.0'
short_description: Manages firmware upgrades on Opengear devices
description:
  -  Manages firmware upgrades on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description:  Manage firmware upgrades on Opengear devices
    type: dict
    suboptions:
      version:
        type: str
        description: The desired firmware version. If the device is already running
          this version the module will return changed=false.
      firmware_image:
        type: str
        description: URL or local path on the control node to the firmware image (.raucb file).
      ignore_version:
        type: bool
        default: false
        description: Ignore firmware version compatibility checks during installation.
      erase_config:
        type: bool
        default: false
        description: Erase device configuration during upgrade rather than migrating it.
          Use with caution as this will reset the device to factory defaults.
  state:
    description:
      - merged - initiate firmware upgrade if current version differs from desired version.
      - gathered - return current firmware version and upgrade status.
    type: str
    choices:
    - merged
    - gathered
    default: merged
notes:
  - Firmware upgrade causes the device to reboot. The module returns changed=true
    once the upgrade is initiated.
  - Use state=gathered to check current version and upgrade status.
  - Diff output shows the expected version change. Use state=gathered after the
    device comes back online to verify the actual installed version.
"""

EXAMPLES = """
- name: Gather firmware facts
  opengear.ng.system_firmware_upgrade:
    state: gathered
  register: firmware

- name: Upgrade firmware using a local image
  opengear.ng.system_firmware_upgrade:
    config:
      version: "25.11.4"
      firmware_image: "/tmp/firmware.raucb"
    state: merged
  register: upgrade

- name: Upgrade firmware from a URL
  opengear.ng.system_firmware_upgrade:
    config:
      version: "25.11.4"
      firmware_image: "https://example.com/firmware.raucb"
    state: merged

- name: Upgrade firmware ignoring version check
  opengear.ng.system_firmware_upgrade:
    config:
      version: "25.11.4"
      firmware_image: "{{ firmware_image_path }}"
      ignore_version: true
    state: merged

- name: Upgrade firmware and erase configuration
  opengear.ng.system_firmware_upgrade:
    config:
      version: "25.11.4"
      firmware_image: "{{ firmware_image_path }}"
      erase_config: true
    state: merged
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_firmware_upgrade import SystemFirmwareUpgradeArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system_firmware_upgrade import SystemFirmwareUpgrade


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemFirmwareUpgradeArgs.argument_spec,
                           supports_check_mode=True)

    result = SystemFirmwareUpgrade(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

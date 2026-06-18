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
module: firmware_upgrade
version_added: '1.0.0'
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
- name: Upgrade firmware to version 25.11.0 using a URL
  opengear.ng.firmware_upgrade:
    config:
      version: "25.11.0"
      firmware_image: "{{ firmware_image_url }}"
    state: merged
  register: upgrade

- name: Upgrade firmware using a local image file
  opengear.ng.firmware_upgrade:
    config:
      version: "25.11.0"
      firmware_image: "/tmp/firmware.raucb"
    state: merged
  register: upgrade

- name: Upgrade firmware with config erase
  opengear.ng.firmware_upgrade:
    config:
      version: "25.11.0"
      firmware_image: "/tmp/firmware.raucb"
      erase_config: true
    state: merged
  register: upgrade

- name: Upgrade firmware ignoring version check
  opengear.ng.firmware_upgrade:
    config:
      version: "25.11.0"
      firmware_image: "/tmp/firmware.raucb"
      ignore_version: true
    state: merged
  register: upgrade

- name: Wait for firmware upgrade to complete
  opengear.ng.firmware_upgrade:
    state: gathered
  register: status
  failed_when: false
  until: >
    (status.gathered | default({})).get('upgrade_status', {}).get('state', '') not in ['pending', 'running']
  retries: 10
  delay: 10
  when: upgrade.changed

- name: Wait for device to come back online
  opengear.ng.firmware_upgrade:
    state: gathered
  register: final_status
  failed_when: false
  until: final_status.gathered is defined
  retries: 30
  delay: 10
  when: upgrade.changed

- name: Verify upgrade succeeded
  ansible.builtin.assert:
    that:
      - final_status.gathered.upgrade_status is none or
        final_status.gathered.upgrade_status.state != 'error'
    fail_msg: "Firmware upgrade failed: {{ final_status.gathered.upgrade_status.error_message | default('unknown error') }}"
  when: upgrade.changed

- name: Verify firmware version
  assert:
    that:
      - final_status.gathered.current_version == "25.11.0"
  when: upgrade.changed
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.firmware_upgrade import FirmwareUpgradeArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.firmware_upgrade import FirmwareUpgrade


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=FirmwareUpgradeArgs.argument_spec,
                           supports_check_mode=True)

    result = FirmwareUpgrade(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

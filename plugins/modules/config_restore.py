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
module: config_restore
version_added: '0.1.0'
short_description: Restore device configuration on Opengear devices
description:
  - Restores a previously exported device configuration from a dotnotation
    format file.
  - The configuration file must match the device version and SKU.
  - Use the config_export module to export the current configuration.
author:
  - Opengear (@opengear)
options:
  config:
    description: Configuration restore options.
    type: dict
    suboptions:
      config_file:
        type: str
        description: >
          Local path on the Ansible control node to the configuration file
          in dotnotation format.
  state:
    description:
      - replaced - initiate a configuration restore from the provided file.
      - gathered - return the current restore operation status.
    type: str
    choices:
      - replaced
      - gathered
    default: replaced
notes:
  - Performing a restore may cause the device to be temporarily unreachable.
    Wait for the device to become available before running subsequent tasks.
  - Use state=gathered to poll for restore completion status.
  - The configuration file must have been exported from a device running
    the same firmware version and SKU.
"""

EXAMPLES = """
- name: Restore device configuration
  opengear.ng.config_restore:
    config:
      config_file: "/path/to/config-backup.cfg"
    state: replaced
  register: restore

- name: Wait for restore to complete
  opengear.ng.config_restore:
    state: gathered
  register: status
  until: status.gathered.status != 'in_progress'
  retries: 30
  delay: 10
  failed_when: false
  when: restore.changed

- name: Assert restore succeeded
  ansible.builtin.assert:
    that:
      - status.gathered.status == 'completed'
      - status.gathered.exit_code == 0
  when: restore.changed
"""

RETURN = """
gathered:
  description: The current restore operation status.
  returned: when state is gathered
  type: dict
  contains:
    status:
      description: Current status of the restore operation.
      type: str
    restore_log:
      description: Log output from the restore operation.
      type: str
    exit_code:
      description: Exit code of the restore operation. 0 indicates success.
      type: int
    restore_status:
      description: Detailed restore status identifier.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.config_restore import ConfigRestoreArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.config_restore import ConfigRestore


def main():
    """
    Main entry point for module execution.

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=ConfigRestoreArgs.argument_spec,
        supports_check_mode=True,
    )

    result = ConfigRestore(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

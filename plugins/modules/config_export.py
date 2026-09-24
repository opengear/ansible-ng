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
module: config_export
version_added: '0.1.0'
short_description: Export device configuration from Opengear devices
description:
  - Exports the current device configuration in dotnotation format.
  - The exported configuration can be saved to a file and used with
    the config_restore module to restore the configuration to a device.
author:
  - Opengear (@opengear)
options:
  state:
    description:
      - gathered - return the current device configuration in dotnotation format.
    type: str
    choices:
      - gathered
    default: gathered
notes:
  - The exported configuration is in dotnotation format, which is the native
    configuration format for Opengear devices.
  - The exported configuration can be edited before restoring, allowing
    selective configuration changes to be applied.
  - Use the config_restore module to apply the configuration back to a device.
"""

EXAMPLES = """
- name: Export device configuration
  opengear.ng.config_export:
    state: gathered
  register: result

- name: Save configuration to file
  ansible.builtin.copy:
    content: "{{ result.gathered }}"
    dest: "/path/to/config-backup.cfg"
    mode: '0644'
"""

RETURN = """
gathered:
  description: The current device configuration in dotnotation format.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.config_export import ConfigExportArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.config_export import ConfigExport


def main():
    """
    Main entry point for module execution.

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=ConfigExportArgs.argument_spec,
        supports_check_mode=True,
    )

    result = ConfigExport(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

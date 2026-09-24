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
module: system_factory_reset
version_added: '0.1.0'
short_description: Erases the configuration of an Opengear appliance
description:
  - Erases the configuration of an Opengear appliance, restoring it to factory
    defaults.
  - This is a destructive, irreversible action. The module always reports
    C(changed) and always triggers an erase unless running in check mode.
  - Under check mode the erase request is not sent.
  - The device reboots immediately after the erase. Subsequent tasks must wait
    for the device to come back online before proceeding.
author:
  - Opengear (@opengear)
options: {}
"""

EXAMPLES = """
- name: Erase device configuration and restore factory defaults
  opengear.ng.system_factory_reset:
  register: reset
"""

RETURN = """
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_factory_reset import SystemFactoryResetArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system_factory_reset import SystemFactoryReset


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemFactoryResetArgs.argument_spec,
                           supports_check_mode=True)

    result = SystemFactoryReset(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

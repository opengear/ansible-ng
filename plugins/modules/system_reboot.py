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
module: system_reboot
version_added: '0.1.0'
short_description: Reboots an Opengear appliance
description:
  - Reboots an Opengear appliance.
  - This is an action, not a stateful resource; invoking the module always
    triggers a reboot and always reports C(changed). It takes no options.
  - Under check mode the reboot request is not sent.
author:
  - Opengear (@opengear)
options: {}
"""

EXAMPLES = """
- name: Reboot the appliance
  opengear.ng.system_reboot:
"""

RETURN = """
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_reboot import SystemRebootArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system_reboot import SystemReboot


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemRebootArgs.argument_spec,
                           supports_check_mode=True)

    result = SystemReboot(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

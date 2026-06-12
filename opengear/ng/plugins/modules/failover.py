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
module: failover
version_added: '1.0.0'
short_description: Manages configuration of failover behavior on Opengear devices
description:
  - Manages configuration of failover behavior on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of failover behavior on Opengear devices
    type: dict
    suboptions:
      enabled:
        type: bool
        description: failover enabled or disabled
      probe_physif:
        description: A Failover event occurs if the probe_address is not reachable on this network interface.
        type: str
      probe_address:
        description: Probe address can be an IPv4/6 address or hostname
        type: str

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
- name: Configure failover
  opengear.ng.failover:
    config:
      enabled: true
      probe_address: 8.8.8.8
      probe_physif: net1
    state: merged

- name: Disable failover
  opengear.ng.failover:
    config:
      enabled: false
    state: merged

- name: Gather failover facts
  opengear.ng.facts:
    gather_network_resources:
      - failover
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.failover import FailoverArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.failover import Failover


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=FailoverArgs.argument_spec,
                           supports_check_mode=True)

    result = Failover(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

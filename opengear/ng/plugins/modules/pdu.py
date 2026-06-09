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
module: pdu
version_added: '1.0.0'
short_description: Manages configuration for PDUs connected to Opengear devices
description:
  - Manages configuration for PDUs connected to Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration for PDUs connected to Opengear devices
    type: list
    elements: dict
    suboptions:
      id:
        description: The unique id of the PDU.
        type: str
      name:
        description: A unique user specified name for the PDU.
        type: str
      driver:
        description: The driver to use to control and monitor the PDU.
        type: str
      method:
        description: The method to used to access the PDU, can be 'snmp', 'powerman' or 'shell'.
        type: str
      monitor:
        description: If true the pdu outlets are monitored for any change in status.
        type: bool
      powerman:
        description: The serial specific settings for a PDU.
        type: dict
        suboptions:
          id:
            type: str
            description: id
          username:
            type: str
            description: username
          password:
            type: str
            description: password
          port:
            type: str
            description: port
      shell:
        description: The serial specific settings for a PDU.
        type: dict
        suboptions:
          id:
            type: str
            description: id
          username:
            type: str
            description: username
          password:
            type: str
            description: password
          port:
            type: str
            description: port
      snmp:
        description: The SNMP configuration to access the PDU.
        type: dict
        suboptions:
          id:
            type: str
            description: id
          protocol:
            type: str
            description: tcp of udp
          address:
            type: str
            description: ip address
          port:
            type: int
            description: tcp or udp port
          version:
            type: str
            description: snmp version
          community:
            type: str
            description: community string
          auth_protocol:
            type: str
            description: snmpv3 auth protocol
          auth_password:
            type: str
            description: snmpv3 auth password
          username:
            type: str
            description: snmp username
          engine_id:
            type: str
            description: engine id
          privacy_protocol:
            type: str
            description: snmpv3 privacy protocol
          privacy_password:
            type: str
            description: snmpv3 privacy password
          security_level:
            type: str
            description: security level
  state:
    description:
    - The state of the configuration after module completion.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - gathered
    - rendered
    default: merged
"""

EXAMPLES = """
- name: Configure a PDU via SNMP
  opengear.ng.pdu:
    config:
      - name: rack-pdu-01
        method: snmp
        monitor: true
        snmp:
          address: 192.168.1.50
          version: v2c
          community: public
          port: 161
    state: merged

- name: Configure a PDU via shell
  opengear.ng.pdu:
    config:
      - name: rack-pdu-02
        method: shell
        shell:
          username: admin
          password: "{{ vault_pdu_password }}"
          port: "2300"
    state: merged

- name: Remove all PDU configuration
  opengear.ng.pdu:
    state: deleted

- name: Gather existing PDU configuration
  opengear.ng.pdu:
    state: gathered
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.pdu import PduArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.pdu import Pdu


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=PduArgs.argument_spec,
                           supports_check_mode=True)

    result = Pdu(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

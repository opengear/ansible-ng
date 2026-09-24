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
module: services_snmp_alert_managers
version_added: '0.1.0'
short_description: Manages SNMP Alert Manager configuration on Opengear devices
description:
  - Manages the collection of SNMP Alert Managers an Opengear device sends SNMP alerts to.
  - Each record's identity is the C(address)/C(port)/C(protocol) combination
    matching the multi_field_identifier used by ogcli. Specify all three for
    reliable idempotent management.
  - This replaces the deprecated single-target C(snmp_manager) configuration.
author:
  - Opengear (@opengear)
options:
  config:
    description: The list of SNMP Alert Managers.
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description: The device-assigned unique identifier for this SNMP Alert Manager. Read-only.
      multi_field_identifier:
        type: str
        description: A device-generated string combining address, port and protocol. Read-only.
      name:
        type: str
        description: A free-text label for the SNMP Alert Manager.
      protocol:
        type: str
        choices: [UDP, TCP, UDP6, TCP6]
        description: The transport protocol used to deliver SNMP alert messages.
      address:
        type: str
        description: The IPv4/IPv6 address or domain name of the SNMP Alert Manager.
        required: true
      port:
        type: int
        description: The port the SNMP Alert Manager listens on for alerts. Defaults to 162.
      msg_type:
        type: str
        choices: [TRAP, INFORM]
        description: The type of SNMP message to send. Applies to v2c/v3 only.
      version:
        type: str
        choices: [v1, v2c, v3]
        description: The version of SNMP used to send messages to this SNMP Alert Manager.
      community:
        type: str
        description: The community string used for SNMPv1/SNMPv2c.
      auth_protocol:
        type: str
        description: The encryption algorithm used for authentication with SNMPv3.
      auth_password:
        type: str
        description: The plaintext authentication password used with SNMPv3.
      username:
        type: str
        description: The username used for authentication with SNMPv3.
      engine_id:
        type: str
        description: A unique identifier for the SNMP agent entity, matching the SNMP Alert Manager's engineID.
      privacy_protocol:
        type: str
        description: The encryption algorithm used for privacy with SNMPv3.
      privacy_password:
        type: str
        description: The plaintext privacy password used with SNMPv3.
      security_level:
        type: str
        choices: [noAuthNoPriv, authNoPriv, authPriv]
        description: The User-based Security Model level to use with SNMPv3.
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
- name: Add an SNMP Alert Manager
  opengear.ng.services_snmp_alert_managers:
    config:
      - name: Primary NMS
        protocol: UDP
        address: snmp.example.com
        port: 162
        version: v2c
        msg_type: TRAP
        community: "{{ snmp_community }}"
    state: merged

- name: Replace all SNMP Alert Managers with this single one
  opengear.ng.services_snmp_alert_managers:
    config:
      - name: Primary NMS
        protocol: UDP
        address: snmp.example.com
        port: 162
        version: v2c
        msg_type: TRAP
        community: "{{ snmp_community }}"
    state: overridden

- name: Remove an SNMP Alert Manager
  opengear.ng.services_snmp_alert_managers:
    config:
      - address: snmp.example.com
        port: 162
        protocol: UDP
    state: deleted

- name: Gather services_snmp_alert_managers facts
  opengear.ng.facts:
    gather_network_resources:
      - services_snmp_alert_managers
"""

RETURN = """
before:
  description: The configuration before the module is executed.
  returned: always
  type: list
after:
  description: The configuration after the module is executed.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.services_snmp_alert_managers import ServicesSnmpAlertManagersArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.services_snmp_alert_managers import ServicesSnmpAlertManagers


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=ServicesSnmpAlertManagersArgs.argument_spec,
                           supports_check_mode=True)

    result = ServicesSnmpAlertManagers(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

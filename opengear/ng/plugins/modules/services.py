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
module: services
version_added: '1.0.0'
short_description: Manages configuration of services on Opengear devices
description:
  - Manages configuration of services on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of services on Opengear devices
    type: dict
    suboptions:
      https:
        type: dict
        description: https
        suboptions:
          csr:
            type: dict
            description: csr
            suboptions:
              common_name:
                type: str
                description: common name
              org_unit:
                type: str
                description: org unit
              organization:
                type: str
                description: org
              locality:
                type: str
                description: locale
              state:
                type: str
                description: state
              country:
                type: str
                description: country
              email:
                type: str
                description: email
              key_length:
                type: str
                description: key length
              csr:
                type: str
                description: csr
              challenge_password:
                type: str
                description: challenge password
              private_key:
                type: str
                description: private key
          cert:
            type: str
            description: certificate
      ntp:
        description: ntp configuraiton
        type: dict
        suboptions:
          enabled:
            type: bool
            description: ntp enabled or disabled
          servers:
            description: list of servers
            type: list
            elements: dict
            suboptions:
              value:
                type: str
                description: hostname or ip of ntp server
      lldp:
        type: dict
        description: lldp configuration
        suboptions:
          enabled:
            type: bool
            description: lldp enabled or disabled
          description:
            type: str
            description: description of lldp service
          platform:
            type: str
            description: platform using lldp
          physifs:
            type: str
            description: interfaces using lldp
      snmp_manager:
        type: dict
        description: snmp manager configuraiton
        suboptions:
          protocol:
            type: str
            description: snmp protocol tcp or udp
          address:
            type: str
            description: hostname or address of snmp server
          port:
            type: int
            description: tcp or udp port
          msg_type:
            type: str
            description: snmp message type
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
            description: snmp user name
          engine_id:
            type: str
            description: snmp engine id
          privacy_protocol:
            type: str
            description: snmp privacy protocol
          privacy_password:
            type: str
            description: snmpv3 privacy password
          security_level:
            type: str
            description: snmp securit level
      snmpd:
        type: dict
        description: snmp daemon
        suboptions:
          enabled:
            type: bool
            description: snmpd enabled or disabled
          port:
            type: int
            description: tcp or udp port
          protocol:
            type: str
            description: tcp or udp
          enable_legacy_versions:
            type: bool
            description: enable legacy versions of snmp
          rocommunity:
            type: str
            description: read only community
          rwcommunity:
            type: str
            description: read/write community
          enable_secure_snmp:
            type: bool
            description: enable secure snmp
          security_level:
            type: str
            description: snmpd security level
          security_name:
            type: str
            description: security name
          engine_id:
            type: str
            description: snmp engine id
          auth_protocol:
            type: str
            description: snmpv3 auth protocol
          auth_use_plaintext:
            type: bool
            description: snmpv3 use plaintext password
          auth_password:
            type: str
            description: snmpv3 auth password
          auth_localized_key:
            type: str
            description: snmp local key
          priv_protocol:
            type: str
            description: snmpv3 priv protol
          priv_use_plaintext:
            type: bool
            description: snmp priv use plaintext password
          priv_password:
            type: str
            description: snmpv3 priv password
          priv_localized_key:
            type: str
            description: priv localized key
      ssh:
        type: dict
        description: ssh configuraiton
        suboptions:
          ssh_url_delimiter:
            type: str
            description: ssh url delimiter
          maxstartups_start:
            type: int
            description: max startups
          min_startups_rate:
            type: int
            description: min startups rate
          maxstartups_full:
            type: int
            description: max startups full
          unauthenticated_serial_port_access:
            type: bool
            description: unauth serial port access
      routing:
        type: dict
        description: routing configuration
        suboptions:
          bgpd:
            description: Configuration for the bgp routing daemon.
            type: dict
            suboptions:
              enabled:
                type: bool
                description: bgpd enabled or disabled
          ospfd:
            description: Configuration for the ospf routing daemon.
            type: dict
            suboptions:
              enabled:
                type: bool
                description: ospfd enabled or disabled
          isisd:
            description: Configuration for the isis routing daemon.
            type: dict
            suboptions:
              enabled:
                type: bool
                description: isisd enabled or disabled
          ripd:
            description: Configuration for the rip routing daemon.
            type: dict
            suboptions:
              enabled:
                type: bool
                description: ripd enabled or disabled
      syslog:
        type: list
        description: syslog configuration
        elements: dict
        suboptions:
          id:
            type: str
            description: id
          port:
            type: int
            description: syslog port
          protocol:
            type: str
            description: syslog tcp or udp
          address:
            type: str
            description: syslog server hostname or address
          description:
            type: str
            description: syslog server description
          port_logging_enabled:
            type: bool
            description: serial port logging enabled
          min_severity:
            type: str
            description: min syslog severity
      snmp_alert_managers:
        type: list
        description: snmp alert manager configuration
        elements: dict
        suboptions:
          id:
            type: str
            description: id
          multi_field_identifer:
            type: str
            description: multi field id
          name:
            type: str
            description: snmp alert manager name
          protocol:
            type: str
            description: snmp alert manager tcp or udp
          address:
            type: str
            description: snmp alert manager hostname or address
          port:
            type: int
            description: tcp or udp port
          msg_type:
            type: str
            description: message type
          version:
            type: str
            description: snmp version
          community:
            type: str
            description: community
          auth_protocol:
            type: str
            description: snmpv3 auth protocol
          auth_password:
            type: str
            description: snmpv3 auth password
          username:
            type: str
            description: username
          engine_id:
            type: str
            description: engine id
          privacy_protocol:
            type: str
            description: snmpv3 priv protocol
          privacy_password:
            type: str
            description: snmpv3 priv password
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
- name: Configure NTP servers
  opengear.ng.services:
    config:
      ntp:
        enabled: true
        servers:
          - value: pool.ntp.org
          - value: time.cloudflare.com
    state: merged

- name: Configure SNMP daemon
  opengear.ng.services:
    config:
      snmpd:
        enabled: true
        port: 161
        protocol: udp
        rocommunity: public
        security_level: authPriv
        auth_protocol: SHA
        auth_password: "{{ snmp_auth_password }}"
        priv_protocol: AES
        priv_password: "{{ snmp_priv_password }}"
    state: merged

- name: Configure syslog forwarding
  opengear.ng.services:
    config:
      syslog:
        - address: syslog.example.com
          port: 514
          protocol: udp
          min_severity: warning
          description: Central syslog server
    state: merged

- name: Configure SSH service
  opengear.ng.services:
    config:
      ssh:
        maxstartups_start: 10
        maxstartups_full: 100
        unauthenticated_serial_port_access: false
    state: merged

- name: Gather services facts
  opengear.ng.facts:
    gather_network_resources:
      - services
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.services import ServicesArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.services import Services


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=ServicesArgs.argument_spec,
                           supports_check_mode=True)

    result = Services(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

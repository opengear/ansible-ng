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
module: services_config
version_added: '0.1.0'
short_description: Manages configuration of singleton services on Opengear devices
description:
  - Manages configuration of services on Opengear devices that have a single
    instance on the device (brute force protection, the HTTPS certificate, TFTP,
    NTP, LLDP, snmpd, SSH, routing daemons, web remote access and perifrouted).
  - Remote syslog servers and SNMP alert managers are collections rather than
    singletons and are managed by the dedicated M(opengear.ng.services_syslog) and
    M(opengear.ng.services_snmp_alert_managers) modules.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of singleton services on Opengear devices
    type: dict
    suboptions:
      brute_force_protection:
        type: dict
        description: >
          When enabled, the system watches for multiple failed login attempts and
          temporarily bans the offending IP address for the configured amount of time.
        suboptions:
          ssh_enabled:
            type: bool
            description: Enable or disable watching failed SSH login attempts.
          https_enabled:
            type: bool
            description: Enable or disable watching failed HTTPS login attempts.
          max_retry:
            type: int
            description: The number of failures within C(find_time) minutes required to ban an IP.
          ban_time:
            type: int
            description: The effective ban duration, in seconds.
          find_time:
            type: int
            description: The time interval, in minutes, before now within which failures count towards a ban.
      https_certificate:
        type: dict
        description: Upload a certificate and private key pair for the web server to use.
        suboptions:
          cert:
            type: str
            description: The PEM-encoded certificate.
          key:
            type: str
            description: The PEM-encoded private key.
      lldp:
        type: dict
        description: Configure the Link Layer Discovery Protocol (LLDP) and Cisco Discovery Protocol (CDP) services.
        suboptions:
          enabled:
            type: bool
            description: Enable or disable LLDP/CDP.
          description:
            type: str
            description: Overrides the default system description sent by the network discovery protocol daemon.
          platform:
            type: str
            description: Overrides the CDP platform name.
          portid_subtype:
            type: str
            choices: [macaddress, ifname]
            description: Controls how LLDP advertises port identifiers.
          physifs:
            type: list
            elements: str
            description: The set of physical interfaces to perform LLDP/CDP monitoring on. Empty means all interfaces.
      ntp:
        type: dict
        description: Configure the NTP client.
        suboptions:
          enabled:
            type: bool
            description: Enable or disable the NTP daemon.
          servers:
            type: list
            elements: dict
            description: The list of NTP servers to synchronize with.
            suboptions:
              value:
                type: str
                description: The IPv4/IPv6 address or hostname of the NTP server.
              key:
                type: dict
                description: The authentication key used to securely access this NTP server.
                suboptions:
                  value:
                    type: str
                    description: The key value.
                  index:
                    type: int
                    description: The key ID.
                  format:
                    type: str
                    choices: [ASCII, HEX]
                    description: Whether the key value is ASCII or hexadecimal.
                  algorithm:
                    type: str
                    choices:
                      - MD5
                      - SHA1
                      - SHA256
                      - SHA384
                      - SHA512
                      - SHA3-224
                      - SHA3-256
                      - SHA3-384
                      - SHA3-512
                      - AES128
                      - AES256
                    description: The cryptographic hash function or cipher used to generate and verify the MAC.
      perifrouted:
        type: dict
        description: Configure the Perifrouted service.
        suboptions:
          enabled:
            type: bool
            description: Enable or disable the Perifrouted service.
      routing:
        type: dict
        description: Configure routing daemons on the appliance.
        suboptions:
          bgpd:
            type: dict
            description: Configuration for the BGP routing daemon.
            suboptions:
              enabled:
                type: bool
                description: Enable or disable bgpd.
          isisd:
            type: dict
            description: Configuration for the IS-IS routing daemon.
            suboptions:
              enabled:
                type: bool
                description: Enable or disable isisd.
          ripd:
            type: dict
            description: Configuration for the RIP routing daemon.
            suboptions:
              enabled:
                type: bool
                description: Enable or disable ripd.
          ospfd:
            type: dict
            description: Configuration for the OSPF routing daemon.
            suboptions:
              enabled:
                type: bool
                description: Enable or disable ospfd.
              router_id:
                type: str
                description: A dotted decimal number identifying the OSPF router.
              redistribute_connected:
                type: bool
                description: Advertise directly connected network routes to OSPF neighbours.
              redistribute_static:
                type: bool
                description: Advertise statically defined network routes to OSPF neighbours.
              redistribute_kernel:
                type: bool
                description: Advertise static routes defined in the kernel to OSPF neighbours.
              maximum_paths:
                type: int
                description: Maximum number of parallel equal-cost paths OSPF will install in the routing table.
              managed_by:
                type: str
                description: The user or system responsible for managing this object.
              interfaces:
                type: list
                elements: dict
                description: >
                  Per-interface OSPF parameters. C(name), C(non_broadcast),
                  C(passive), C(auth_method) and C(auth_keys) are required.
                suboptions:
                  name:
                    type: str
                    description: The name of the interface these settings apply to.
                  cost:
                    type: int
                    description: The link cost of the interface used in OSPF route calculations.
                  hello_interval:
                    type: int
                    description: The interval, in seconds, between sending OSPF hello packets over this interface.
                  dead_interval:
                    type: int
                    description: The interval, in seconds, before declaring the neighbor dead.
                  priority:
                    type: int
                    description: Used to determine which OSPF router should be the designated router (DR).
                  area:
                    type: str
                    description: The OSPF area assigned to this interface.
                  non_broadcast:
                    type: bool
                    description: Mark the interface as non broadcast for OSPF purposes.
                  passive:
                    type: bool
                    description: Mark the interface as passive for OSPF purposes.
                  auth_method:
                    type: str
                    choices: [no_auth, cleartext, md5]
                    description: The authentication method to use for communications on this interface.
                  auth_keys:
                    type: list
                    elements: dict
                    description: Authentication keys for the associated auth_method. Required (may be empty).
                    suboptions:
                      id:
                        type: str
                        description: The id of the associated key. Required per entry.
                      key:
                        type: str
                        description: The actual key value. Required per entry.
              neighbors:
                type: list
                elements: dict
                description: Static OSPF neighbor devices for non-broadcast networks.
                suboptions:
                  address:
                    type: str
                    description: The IPv4 host address of the neighbor.
              networks:
                type: list
                elements: dict
                description: IP network configurations to enable the OSPF service for.
                suboptions:
                  address_with_mask:
                    type: str
                    description: An IPv4 network address with CIDR subnet mask to enable OSPF for.
                  area:
                    type: str
                    description: The OSPF area assigned to this network.
      snmpd:
        type: dict
        description: Configure the SNMP daemon (SNMP agent).
        suboptions:
          enabled:
            type: bool
            description: Enable or disable the SNMP service.
          port:
            type: int
            description: The port for the SNMP service to use.
          protocol:
            type: str
            description: The protocol for the SNMP service to use.
          enable_legacy_versions:
            type: bool
            description: Enable SNMPv1 and SNMPv2c.
          rocommunity:
            type: str
            description: The read-only community string.
          rwcommunity:
            type: str
            description: The read-write community string.
          enable_secure_snmp:
            type: bool
            description: Enable SNMPv3.
          security_level:
            type: str
            description: The User-based Security Model level to use (noauth, auth or priv).
          security_name:
            type: str
            description: The username used for authentication with SNMPv3.
          engine_id:
            type: str
            description: A unique identifier for the SNMP agent entity.
          auth_protocol:
            type: str
            description: The encryption algorithm to use for authentication with SNMPv3.
          auth_use_plaintext:
            type: bool
            description: Use a plaintext password for authentication with SNMPv3 instead of a localized key.
          auth_password:
            type: str
            description: The plaintext authentication password to use with SNMPv3.
          auth_localized_key:
            type: str
            description: The localized authentication key for SNMPv3.
          priv_protocol:
            type: str
            description: The encryption algorithm to use for privacy with SNMPv3.
          priv_use_plaintext:
            type: bool
            description: Use a plaintext password for privacy with SNMPv3 instead of a localized key.
          priv_password:
            type: str
            description: The plaintext privacy password to use with SNMPv3.
          priv_localized_key:
            type: str
            description: The localized privacy key for SNMPv3.
      ssh:
        type: dict
        description: Configure the SSH service.
        suboptions:
          ssh_url_delimiter:
            type: str
            description: The character used to separate the username from port selection information.
          maxstartups_start:
            type: int
            description: >
              The SSH daemon rejects a proportion of connection attempts once the number
              of unauthenticated connections reaches this value.
          maxstartups_rate:
            type: int
            description: >
              The probability, as a percentage, that a connection attempt is rejected once
              C(maxstartups_start) is reached.
          maxstartups_full:
            type: int
            description: All connection attempts are refused once the number of unauthenticated connections reaches this value.
          unauthenticated_serial_port_access:
            type: bool
            description: Allow unauthenticated access to all serial ports through SSH.
          alternate_base_port:
            type: int
            description: An alternate base port for serial port IP aliases.
      tftp:
        type: dict
        description: Configure the TFTP server.
        suboptions:
          enabled:
            type: bool
            description: Enable the TFTP service.
          path:
            type: str
            description: The storage location of the TFTP server on disk.
      web:
        type: dict
        description: Configure whether the web server accepts remote connections.
        suboptions:
          allow_remote_access:
            type: bool
            description: >
              When disabled, the web server only accepts connections from the local
              appliance (the loopback interface) and refuses all remote HTTP/HTTPS connections.
              This includes the connection this and any other opengear.ng httpapi-based
              module is using, so setting this to C(false) over a non-loopback connection
              will lock the module out of the device.
  state:
    description:
    - The state of the configuration after module completion.
    - C(merged) and C(replaced) both update only the settings provided;
      unspecified settings are left as-is.
    type: str
    choices:
    - merged
    - replaced
    - gathered
    - rendered
    default: merged
notes:
  - C(ntp.servers) and C(routing.ospfd.interfaces)/C(neighbors)/C(networks) are
    matched by an identity field (server C(value), interface C(name), etc.) On
    C(merged), a matching entry is updated in place, unmatched existing entries
    are kept, and new ones are appended. On C(replaced), the provided list becomes
    the complete list.
"""

EXAMPLES = """
- name: Configure NTP servers
  opengear.ng.services_config:
    config:
      ntp:
        enabled: true
        servers:
          - value: pool.ntp.org
          - value: time.cloudflare.com
    state: merged

- name: Configure SNMP daemon
  opengear.ng.services_config:
    config:
      snmpd:
        enabled: true
        port: 161
        protocol: UDP
        rocommunity: public
        security_level: priv
        auth_protocol: SHA
        auth_password: "{{ snmp_auth_password }}"
        priv_protocol: AES
        priv_password: "{{ snmp_priv_password }}"
    state: merged

- name: Configure SSH service
  opengear.ng.services_config:
    config:
      ssh:
        maxstartups_start: 10
        maxstartups_full: 100
        unauthenticated_serial_port_access: false
    state: merged

- name: Enable brute force protection
  opengear.ng.services_config:
    config:
      brute_force_protection:
        ssh_enabled: true
        https_enabled: true
        max_retry: 5
        ban_time: 600
        find_time: 10
    state: merged

- name: Enable OSPF routing
  opengear.ng.services_config:
    config:
      routing:
        ospfd:
          enabled: true
          router_id: 10.0.0.2
          redistribute_static: true
    state: merged

- name: Gather services_config facts
  opengear.ng.facts:
    gather_network_resources:
      - services_config
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.services_config import ServicesConfigArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.services_config import ServicesConfig


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=ServicesConfigArgs.argument_spec,
                           supports_check_mode=True)

    result = ServicesConfig(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

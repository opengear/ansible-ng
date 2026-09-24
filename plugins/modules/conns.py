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
module: conns
version_added: '0.1.0'
short_description: Manages network connection configuration for Opengear devices
description:
  - Manages network connection configuration for Opengear devices.
  - The device auto-assigns a I(name) and I(id) when a connection is created.
    Use I(gathered) state to discover these values after creation.
  - Connections are matched on subsequent runs using I(id) first, then I(name).
    If neither matches, the module falls back to matching by static IP address
    (I(ipv4_static_settings.address) or I(ipv6_static_settings.address)).
    This fallback is essential for idempotent I(merged), I(replaced), and
    I(deleted) operations when the device-assigned name is not known.
  - For I(deleted) state, always include the IP address alongside the name
    to ensure the correct connection is found even if the device-assigned name
    differs from what was specified at creation time.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manages network connection configuration for Opengear devices.
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description: Unique identifier of the connection (e.g. C(system_net_conns-1)).
      name:
        type: str
        description:
          - Connection name. The device auto-assigns this on creation; it cannot
            be set by the user. Provide the device-assigned name (from I(gathered)
            state) for reliable look-up. If the name does not match any existing
            connection, the module falls back to matching by IP address.
      description:
        type: str
        description: Human-readable label for the connection.
      mode:
        type: str
        description: IP configuration mode for the connection.
        choices: [static, ipv6_static, dhcp, ipv6_automatic]
      physif:
        type: str
        description:
          - Physical interface this connection is attached to.
            Accepts a device name (e.g. C(net1)) or an interface ID
            (e.g. C(system_net_physifs-1)).
      ipv4_static_settings:
        type: dict
        description: IPv4 static address settings. Used when I(mode) is C(static).
        suboptions:
          address:
            type: str
            description: IPv4 address.
          netmask:
            type: str
            description: Subnet mask (e.g. C(255.255.255.0)).
          broadcast:
            type: str
            description: Broadcast address.
          gateway:
            type: str
            description: Default gateway address.
          dns1:
            type: str
            description:
              - Primary DNS server. Deprecated since October 2021.
                Use I(physif.dns.nameservers) instead.
          dns2:
            type: str
            description:
              - Secondary DNS server. Deprecated since October 2021.
                Use I(physif.dns.nameservers) instead.
      ipv6_static_settings:
        type: dict
        description: IPv6 static address settings. Used when I(mode) is C(ipv6_static).
        suboptions:
          address:
            type: str
            description: IPv6 address.
          prefix_length:
            type: int
            description: Prefix length (e.g. C(64)).
          gateway:
            type: str
            description: IPv6 default gateway address.
          dns1:
            type: str
            description:
              - Primary DNS server. Deprecated since October 2021.
                Use I(physif.dns.nameservers) instead.
          dns2:
            type: str
            description:
              - Secondary DNS server. Deprecated since October 2021.
                Use I(physif.dns.nameservers) instead.
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
# The device auto-assigns a name to each connection on creation.
# Use 'gathered' state to discover the device-assigned name and id.
# For idempotent merged/replaced/deleted operations, the module falls back
# to matching by IP address when the name does not match any existing connection.

- name: Gather connection facts to discover device-assigned names
  opengear.ng.conns:
    state: gathered
  register: conns_facts

- name: Configure a static IPv4 connection (idempotent via IP fallback)
  opengear.ng.conns:
    config:
      - name: default-conn-1
        description: Static management connection
        mode: static
        physif: net1
        ipv4_static_settings:
          address: 192.168.1.2
          netmask: 255.255.255.0
          broadcast: 192.168.1.255
          gateway: 192.168.1.1
    state: merged

- name: Configure a DHCP connection
  opengear.ng.conns:
    config:
      - name: default-conn-2
        description: DHCP connection on net2
        mode: dhcp
        physif: net2
    state: merged

- name: Configure a static IPv6 connection
  opengear.ng.conns:
    config:
      - name: default-conn-1
        mode: ipv6_static
        physif: net1
        ipv6_static_settings:
          address: 2001:db8::1
          prefix_length: 64
          gateway: 2001:db8::fffe
    state: merged

# Always include the IP address when deleting a static connection.
# If the device-assigned name differs from what you specified at creation,
# the IP address is used as a fallback to locate the correct connection.
- name: Delete a static connection by IP address
  opengear.ng.conns:
    config:
      - name: default-conn-1
        ipv4_static_settings:
          address: 192.168.1.2
    state: deleted

- name: Gather connection facts via facts module
  opengear.ng.facts:
    gather_network_resources:
      - conns
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.conns import ConnsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.conns import Conns


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=ConnsArgs.argument_spec, supports_check_mode=True
    )

    result = Conns(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

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
module: physifs
version_added: '0.1.0'
short_description: Manages configuration of physical interfaces on Opengear devices
description:
  - Manages configuration of physical interfaces on Opengear devices.
  - Interfaces are identified by I(id) (e.g. C(system_net_physifs-1)) or I(name)
    (e.g. C(init_net1)). Provide at least one; I(name) is read-only on existing
    interfaces and is used only for look-up.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of physical interfaces on Opengear devices.
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description: Unique identifier of the interface (e.g. C(system_net_physifs-1)).
      name:
        type: str
        description:
          - System name of the interface (e.g. C(init_net1)). Read-only on existing
            interfaces; used for identification when I(id) is not supplied.
      enabled:
        type: bool
        description: Enable or disable the interface.
      description:
        type: str
        description: Human-readable label for the interface.
      media:
        type: str
        description: Media type of the interface.
        choices: [ethernet, cellular, bridge, bond, vlan, loopback]
      mtu:
        type: int
        description: Maximum transmission unit in bytes.
      device:
        type: str
        description:
          - Kernel device name (e.g. C(net1)). Required when creating new aggregate
            interfaces such as bonds, bridges, or VLANs.
      slaves:
        type: list
        elements: str
        description: Kernel device names of slave interfaces for bond and bridge media types.
      dns:
        type: dict
        description: Interface-level DNS settings (preferred over the deprecated conn dns1/dns2).
        suboptions:
          nameservers:
            type: list
            elements: str
            description: List of DNS nameserver addresses.
          search_domains:
            type: list
            elements: str
            description: List of DNS search domains.
      ethernet_setting:
        type: dict
        description: Settings specific to ethernet interfaces.
        suboptions:
          link_speed:
            type: str
            description: Ethernet link speed and duplex.
            choices: [auto, 1000mbps-fd, 100mbps-hd, 100mbps-fd, 10mbps-hd, 10mbps-fd]
      cellular_setting:
        type: dict
        description: Settings specific to cellular interfaces.
        suboptions:
          active_sim:
            type: int
            description: Slot number of the active SIM (1 or 2).
          sim_failover_policy:
            type: str
            description: When to fail over to the secondary SIM.
            choices: [never, on_disconnect]
          sim_failover_disconnect_mode:
            type: str
            description: Method used to detect disconnect for SIM failover.
            choices: [ping]
          sim_failback_policy:
            type: str
            description: When to fail back to the primary SIM.
            choices: [never, delayed, on_disconnect]
          sim_failback_disconnect_mode:
            type: str
            description: Method used to detect disconnect for SIM failback.
            choices: [ping]
          sims:
            type: list
            elements: dict
            description: Per-SIM configuration.
            suboptions:
              slot:
                type: int
                description: SIM slot number.
              apn:
                type: str
                description: Access Point Name.
              username:
                type: str
                description: APN authentication username.
              password:
                type: str
                description: APN authentication password.
              iptype:
                type: str
                description: IP version requested from the network.
                choices: [IPv4, IPv6, IPv4v6]
              authtype:
                type: str
                description: APN authentication protocol.
                choices: [none, pap, chap, pap-chap]
              ipv4_netmask:
                type: str
                description: Static IPv4 netmask (rarely required; leave unset for dynamic).
              mtu:
                type: int
                description: MTU for this SIM's connection.
              carrier_firmware:
                type: str
                description: Carrier firmware profile identifier.
              failback_delay:
                type: int
                description: Seconds to wait before failing back to this SIM.
              fail_probe_address:
                type: str
                description: Address probed to detect SIM connectivity loss.
              fail_probe_interval:
                type: int
                description: Interval in seconds between connectivity probes.
              fail_probe_count:
                type: int
                description: Number of consecutive probe failures before failover.
              fail_probe_threshold:
                type: int
                description: Probe failure threshold.
      bond_setting:
        type: dict
        description: Settings specific to bond interfaces.
        suboptions:
          mode:
            type: str
            description: Bonding mode.
            choices: [balance-rr, active-backup, balance-xor, broadcast, 802.3ad, balance-tlb, balance-alb]
          poll_interval:
            type: int
            description: MII link monitoring interval in milliseconds.
          primary_slave:
            type: str
            description: Device name of the preferred active slave in active-backup mode.
      bridge_setting:
        type: dict
        description: Settings specific to bridge interfaces.
        suboptions:
          stp_enabled:
            type: bool
            description: Enable Spanning Tree Protocol on the bridge.
          primary_slave:
            type: str
            description: Device name of the primary bridge member.
      vlan_setting:
        type: dict
        description: Settings specific to VLAN interfaces.
        suboptions:
          parent_physif:
            type: str
            description: ID or name of the parent physical interface.
          vlan_id:
            type: int
            description: 802.1Q VLAN ID (1–4094).
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
- name: Configure an ethernet interface by name
  opengear.ng.physifs:
    config:
      - name: init_net1
        enabled: true
        description: Primary management interface
        mtu: 1500
        media: ethernet
        ethernet_setting:
          link_speed: auto
    state: merged

- name: Configure a cellular interface with dual SIM failover
  opengear.ng.physifs:
    config:
      - name: init_wwan0
        enabled: true
        description: Primary cellular interface
        media: cellular
        cellular_setting:
          active_sim: 1
          sim_failover_policy: on_disconnect
          sim_failover_disconnect_mode: ping
          sim_failback_policy: delayed
          sims:
            - slot: 1
              apn: internet
              iptype: IPv4
              fail_probe_address: 8.8.8.8
              fail_probe_count: 5
              fail_probe_interval: 30
            - slot: 2
              apn: backup.internet
              iptype: IPv4
              fail_probe_address: 8.8.8.8
              fail_probe_count: 5
              fail_probe_interval: 30
    state: merged

- name: Configure a VLAN interface
  opengear.ng.physifs:
    config:
      - name: init_net1
        device: net1.100
        description: VLAN 100
        media: vlan
        vlan_setting:
          parent_physif: init_net1
          vlan_id: 100
    state: merged

- name: Configure a bond interface
  opengear.ng.physifs:
    config:
      - device: bond0
        description: Active-backup bond
        media: bond
        slaves:
          - net1
          - net2
        bond_setting:
          mode: active-backup
          primary_slave: net1
          poll_interval: 100
    state: merged

- name: Set interface-level DNS servers
  opengear.ng.physifs:
    config:
      - name: init_net1
        dns:
          nameservers:
            - 8.8.8.8
            - 8.8.4.4
          search_domains:
            - example.com
    state: merged

- name: Delete a specific interface by name
  opengear.ng.physifs:
    config:
      - name: init_net1
    state: deleted

- name: Gather physical interface facts
  opengear.ng.physifs:
    state: gathered

- name: Gather physical interface facts via facts module
  opengear.ng.facts:
    gather_network_resources:
      - physifs
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.physifs import PhysifsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.physifs import Physifs


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=PhysifsArgs.argument_spec, supports_check_mode=True
    )

    result = Physifs(module).execute_module()
    for warning in result.pop("warnings", []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == "__main__":
    main()

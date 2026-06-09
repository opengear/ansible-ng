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
module: physifs
version_added: '1.0.0'
short_description: Manages configuration of physical interfaces on Opengear devices
description:
  - Manages configuration of physical interfaces on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of physical interfaces on Opengear devices
    type: list
    elements: dict
    suboptions:
      enabled:
        type: bool
        description: enabled or disabled
      name:
        type: str
        description: interface name
      id:
        type: str
        description: id
      mtu:
        type: int
        description: mtu size
      description:
        type: str
        description: interface description
      media:
        type: str
        description: media type
      slaves:
        type: list
        description: slave interfaces
        elements: str
      bond_setting:
        type: dict
        description: bond configuration
        suboptions:
          mode:
            type: str
            description: bond mode
          poll_interval:
            type: int
            description: poll interval
          primary_slave:
            type: str
            description: primary slave interface
      bridge_setting:
        type: dict
        description: bridge configuration
        suboptions:
          stp_enabled:
            type: bool
            description: stp enabled or disabled on bridge
          primary_slave:
            type: str
            description: primary slave interface on bridge
      vlan_setting:
        type: dict
        description: vlan configuration
        suboptions:
          parent_physif:
            type: str
            description: parent interface
          vlan_id:
            type: int
            description: vlan id
      cellular_setting:
        type: dict
        description: cellular configuration
        suboptions:
          id:
            type: str
            description: id
          active_sim:
            type: int
            description: active sim
          sim_failover_policy:
            type: str
            description: sim failover policy
          sim_failover_disconnect_mode:
            type: str
            description: sim failover disconnect mode
          sim_failback_policy:
            type: str
            description: sim failback policy
          sim_failback_disconnect_mode:
            type: str
            description: sim failback disconnect mode
          sims:
            type: list
            description: sim
            elements: dict
            suboptions:
              id:
                type: str
                description: id
              slot:
                type: int
                description: slot
              apn:
                type: str
                description: apn
              username:
                type: str
                description: username
              password:
                type: str
                description: password
              iptype:
                type: str
                description: iptype
              failback_delay:
                type: int
                description: failback delay
              fail_probe_address:
                type: str
                description: probe address
              fail_probe_interval:
                type: int
                description: probe interval
              fail_probe_count:
                type: int
                description: probe count
              fail_probe_threshold:
                type: int
                description: probe threshold
      ethernet_setting:
        type: dict
        description: ethernet configuration
        suboptions:
          link_speed:
            type: str
            description: link speed
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
- name: Configure a physical ethernet interface
  opengear.ng.physifs:
    config:
      - id: physif-1
        enabled: true
        description: Primary management interface
        mtu: 1500
        ethernet_setting:
          link_speed: auto

- name: Configure a cellular interface with dual SIM
  opengear.ng.physifs:
    config:
      - id: physif-cellular1
        enabled: true
        description: Primary cellular interface
        cellular_setting:
          active_sim: 1
          sim_failover_policy: automatic
          sim_failback_policy: automatic
          sims:
            - slot: 1
              apn: internet
              iptype: ipv4
              fail_probe_address: 8.8.8.8
              fail_probe_count: 5
              fail_probe_interval: 30
            - slot: 2
              apn: backup.internet
              iptype: ipv4
              fail_probe_address: 8.8.8.8
              fail_probe_count: 5
              fail_probe_interval: 30
    state: merged

- name: Configure a VLAN interface
  opengear.ng.physifs:
    config:
      - id: physif-vlan100
        enabled: true
        description: VLAN 100
        vlan_setting:
          parent_physif: physif-1
          vlan_id: 100
    state: merged

- name: Gather physical interface facts
  opengear.ng.facts:
    gather_network_resources:
      - physifs
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.ng.plugins.module_utils.argspec.physifs import PhysifsArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.physifs import Physifs


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=PhysifsArgs.argument_spec,
                           supports_check_mode=True)

    result = Physifs(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

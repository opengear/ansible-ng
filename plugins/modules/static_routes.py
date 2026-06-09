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
module: static_routes
short_description: Manages configuration of static routes on Opengear devices
version_added: '1.0.0'
description:
  - Manages configuration of static routes on Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of services on Opengear devices
    type: list
    elements: dict
    suboptions:
      id:
        description: Unique id of item.
        type: str
      description:
        description: A description for the static route.
        type: str
      destination_address:
        description: The destination network/host that the route provides access to.
        type: str
      destination_netmask:
        description: Netmask for IPv4/IPv6 (CIDR format).
        type: int
      gateway_address:
        description: The IPv4/IPv6 address of the router gateway that will route packets to the destination address.
        type: str
      interface:
        description: The network interface to be associated with the route.
        type: str
      metric:
        description: The route metric, which represents the cost of routing packets via this route.
        type: int

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
- name: Add a static route
  opengear.ng.static_routes:
    config:
      - destination_address: 192.168.10.0
        destination_netmask: 24
        gateway_address: 10.0.0.1
        interface: eth0
        description: Route to office LAN
        metric: 100
    state: merged

- name: Add multiple static routes
  opengear.ng.static_routes:
    config:
      - destination_address: 192.168.10.0
        destination_netmask: 24
        gateway_address: 10.0.0.1
        interface: eth0
        description: Route to office LAN
        metric: 100
      - destination_address: 172.16.0.0
        destination_netmask: 16
        gateway_address: 10.0.0.1
        interface: eth0
        description: Route to management network
        metric: 100
    state: merged

- name: Replace all static routes with a defined set
  opengear.ng.static_routes:
    config:
      - destination_address: 0.0.0.0
        destination_netmask: 0
        gateway_address: 10.0.0.1
        interface: eth0
        description: Default gateway
        metric: 100
    state: overridden

- name: Delete a specific static route by id
  opengear.ng.static_routes:
    config:
      - id: "route-1"
    state: deleted

- name: Delete all static routes
  opengear.ng.static_routes:
    state: deleted

- name: Gather existing static routes
  opengear.ng.static_routes:
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.static_routes import StaticRoutesArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.static_routes import StaticRoutes


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=StaticRoutesArgs.argument_spec,
                           supports_check_mode=True)

    result = StaticRoutes(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

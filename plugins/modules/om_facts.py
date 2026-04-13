#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'opengear'}


DOCUMENTATION = """
---
module: om_facts
version_added: '1.0.0'
short_description: Get facts about om devices.
description:
  - Collects facts from network devices running the om operating system.
author:
  - Opengear (@opengear)
options:
  gather_subset:
    description:
      - When supplied, this argument will restrict the facts collected to a given subset.
    required: false
    type: list
    elements: str
    default: 'all'
    version_added: '1.0.0'
  gather_network_resources:
    description:
      - When supplied, this argument will restrict the facts collected to a given subset.
    required: false
    type: list
    elements: str
    choices:
      - all
      - auth
      - conns
      - groups
      - physifs
      - ports
      - pdu
      - services
      - static_routes
      - system
      - users
    version_added: '1.0.0'
"""

EXAMPLES = """
- name: Gather all om facts
  opengear.om.om_facts:
    gather_subset: all

- name: Gather system facts only
  opengear.om.om_facts:
    gather_network_resources:
      - system
"""

RETURN = """
ansible_network_resources:
  description: Facts gathered from the device.
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.facts.facts import FactsArgs
from ansible_collections.opengear.om.plugins.module_utils.network.om.facts.facts import Facts


def main():
    """
    Main entry point for module execution

    :returns: ansible_facts
    """
    module = AnsibleModule(argument_spec=FactsArgs.argument_spec,
                           supports_check_mode=True)
    warnings = ['default value for `gather_subset` '
                'will be changed to `min` from `!config` v2.11 onwards']

    result = Facts(module).get_facts()

    ansible_facts, additional_warnings = result
    warnings.extend(additional_warnings)

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()

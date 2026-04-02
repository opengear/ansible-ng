#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'opengear',
}

DOCUMENTATION = """
---
module: om_banner
version_added: 1.0.5
short_description: Manages the login banner on Opengear OM devices
description:
  - Manages the login banner text displayed on Opengear OM & CM8100 devices.
author:
  - "Adrian Van Katwyk (@avankatwyk)"
options:
  config:
    description: The banner configuration.
    type: dict
    suboptions:
      banner:
        type: str
        description: The login banner text.
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
    - parsed
    default: merged
"""

EXAMPLES = """
- name: Set the login banner
  opengear.om.om_banner:
    config:
      banner: "Authorized access only."
    state: merged

- name: Remove the login banner
  opengear.om.om_banner:
    state: deleted

- name: Gather the current banner
  opengear.om.om_banner:
    state: gathered
"""

RETURN = """
before:
  description: The configuration before the module invocation.
  returned: always
  type: dict
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.banner.banner import BannerArgs
from ansible_collections.opengear.om.plugins.module_utils.network.om.config.banner.banner import Banner


def main():
    module = AnsibleModule(
        argument_spec=BannerArgs.argument_spec,
        supports_check_mode=True,
    )
    result = Banner(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

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
module: auth
version_added: '1.0.0'
short_description: Manages auth configuration for Opengear devices
description:
  - Manages auth configuration for Opengear devices
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage auth configuration for Opengear devices
    type: dict
    suboptions:
      mode:
        type: str
        description: auth mode
      policy:
        description: Check local credentials after remote auth failure.
        type: str
      tacacsMethod:
        type: str
        description: tacacs method
      tacacsService:
        type: str
        description: tacacs service
      ldapBaseDN:
        type: str
        description: ldap base dn
      ldapBindDN:
        type: str
        description: ldap bind dn
      ldapIgnoreReferals:
        type: bool
        description: ldap ignore referrals
      ldapUsernameAttribute:
        type: str
        description: ldap username
      ldapGroupMembershipAttribute:
        type: str
        description: ldap group member
      radiusAuthenticationServers:
        type: list
        description: radius auth servers
        elements: dict
        suboptions:
          id:
            type: str
            description: id
          hostname:
            type: str
            description: hostname or address
          port:
            type: int
            description: radius port
      radiusAccountingServers:
        type: list
        description: radius accounting server
        elements: dict
        suboptions:
          id:
            type: str
            description: id
          hostname:
            type: str
            description: hostname or address
          port:
            type: int
            description: port
      tacacsAuthenticationServers:
        type: list
        description: tacacs auth server
        elements: dict
        suboptions:
          id:
            type: str
            description: id
          hostname:
            type: str
            description: hostname or address
          port:
            type: int
            description: port
      ldapAuthenticationServers:
        type: list
        description: ldap auth server
        elements: dict
        suboptions:
          id:
            type: str
            description: id
          hostname:
            type: str
            description: hostname or address
          port:
            type: int
            description: port
      radiusPassword:
        type: str
        description: radius password
      tacacsPassword:
        type: str
        description: tacacs password
      ldapBindPassword:
        type: str
        description: ldap bind password
  state:
    description:
    - The state of the configuration after module completion.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - gathered
    - rendered
    default: merged
"""

EXAMPLES = """
- name: Configure LDAP authentication
  opengear.ng.auth:
    config:
      mode: ldap
      policy: remotelocal
      timeout: 10
      ldapBaseDN: dc=example,dc=com
      ldapBindDN: cn=admin,dc=example,dc=com
      ldapIgnoreReferrals: true
      ldapUsernameAttribute: uid
      ldapGroupMembershipAttribute: gid
      ldapBindPassword: "{{ ldap_bind_password }}"
      ldapAuthenticationServers:
        - hostname: ldap.example.com
          port: 389
        - hostname: ldap2.example.com
          port: 389
    state: merged

- name: Gather auth facts
  opengear.ng.facts:
    gather_network_resources:
      - auth
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.auth import AuthArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.auth import Auth


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=AuthArgs.argument_spec,
                           supports_check_mode=True)

    result = Auth(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

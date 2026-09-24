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
module: auth
version_added: '0.1.0'
short_description: Manages auth configuration for Opengear devices
description:
  - Manages authentication configuration for Opengear devices, including local,
    RADIUS, TACACS+, and LDAP authentication modes.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage auth configuration for Opengear devices
    type: dict
    suboptions:
      mode:
        type: str
        description: Authentication mode
        choices: ['local', 'radius', 'tacacs', 'ldap']
      policy:
        description: |
          Fallback policy for remote authentication.
          C(remotedownlocal) falls back to local only when the remote server is unreachable.
          C(remotelocal) always checks local credentials after remote authentication.
        type: str
        choices: ['remotedownlocal', 'remotelocal']
      timeout:
        type: int
        description: Timeout in seconds for remote authentication server responses (1-3600).
      radiusMethod:
        type: str
        description: RADIUS authentication method.
        choices: ['pap', 'mschapv2']
      radiusAuthenticationServers:
        type: list
        description: List of RADIUS authentication servers.
        elements: dict
        suboptions:
          id:
            type: str
            description: Server ID (read-only, assigned by device).
          hostname:
            type: str
            description: Hostname or IP address of the RADIUS server.
          port:
            type: int
            description: UDP port for the RADIUS server.
      radiusAccountingServers:
        type: list
        description: List of RADIUS accounting servers.
        elements: dict
        suboptions:
          id:
            type: str
            description: Server ID (read-only, assigned by device).
          hostname:
            type: str
            description: Hostname or IP address of the RADIUS accounting server.
          port:
            type: int
            description: UDP port for the RADIUS accounting server.
      radiusAccountingEnabled:
        type: bool
        description: Enable RADIUS accounting.
      radiusRequireMessageAuthenticator:
        type: bool
        description: Require the Message-Authenticator attribute in RADIUS responses.
      radiusPassword:
        type: str
        description: Shared secret for RADIUS servers. Write-only; not returned by the device.
      tacacsMethod:
        type: str
        description: TACACS+ authentication method.
        choices: ['pap', 'chap', 'login']
      tacacsService:
        type: str
        description: TACACS+ service type (default C(raccess)).
      tacacsAuthenticationServers:
        type: list
        description: List of TACACS+ authentication servers.
        elements: dict
        suboptions:
          id:
            type: str
            description: Server ID (read-only, assigned by device).
          hostname:
            type: str
            description: Hostname or IP address of the TACACS+ server.
          port:
            type: int
            description: TCP port for the TACACS+ server.
      tacacsAccountingEnabled:
        type: bool
        description: Enable TACACS+ accounting.
      tacacsPassword:
        type: str
        description: Shared secret for TACACS+ servers. Write-only; not returned by the device.
      ldapBaseDN:
        type: str
        description: Base DN for LDAP searches.
      ldapBindDN:
        type: str
        description: Bind DN used for LDAP authentication.
      ldapBindPassword:
        type: str
        description: Password for the LDAP bind DN. Write-only; not returned by the device.
      ldapAuthenticationServers:
        type: list
        description: List of LDAP authentication servers.
        elements: dict
        suboptions:
          id:
            type: str
            description: Server ID (read-only, assigned by device).
          hostname:
            type: str
            description: Hostname or IP address of the LDAP server.
          port:
            type: int
            description: TCP port for the LDAP server.
      ldapUsernameAttribute:
        type: str
        description: LDAP attribute used to match the username.
      ldapGroupMembershipAttribute:
        type: str
        description: LDAP attribute used to determine group membership.
      ldapIgnoreReferrals:
        type: bool
        description: Ignore LDAP referrals during authentication.
      ldapSslMode:
        type: str
        description: SSL/TLS mode for LDAP connections.
        choices: ['ldap_only', 'ldaps_preferred', 'ldaps_only']
      ldapSslIgnoreCertErrors:
        type: bool
        description: Ignore SSL certificate validation errors for LDAP connections.
      ldapSslCaCert:
        type: str
        description: CA certificate (PEM format) used to validate the LDAP server's SSL certificate.
  state:
    description:
    - The state of the configuration after module completion.
    - C(merged) merges the provided config into the existing config; want fields overwrite have fields.
    - C(replaced) and C(overridden) fully replace the auth config with the provided values.
    - C(gathered) retrieves the current auth configuration from the device.
    - C(rendered) generates commands without connecting to a device.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - gathered
    - rendered
    default: merged
notes:
  - Diff output shows the expected configuration change based on the commands
    generated. It does not reflect the actual device state after execution,
    which may differ due to device-side normalization or concurrent changes.
    Use state=gathered after a run to verify the actual device state.
  - Sensitive fields (radiusPassword, tacacsPassword, ldapBindPassword) are
    write-only; they are never returned by the device and will not appear in
    diff or after output. Specifying a sensitive field always triggers a PUT
    even if no other fields changed.
  - Server list fields (radiusAuthenticationServers, radiusAccountingServers,
    tacacsAuthenticationServers, ldapAuthenticationServers) always trigger a
    PUT when specified in merged state, since device-assigned id fields prevent
    reliable idempotency comparison.
"""

EXAMPLES = """
- name: Gather auth facts
  opengear.ng.facts:
    gather_network_resources:
      - auth
  register: auth_facts

- name: Show auth facts
  ansible.builtin.debug:
    var: auth_facts

- name: Set local authentication
  opengear.ng.auth:
    config:
      mode: local
    state: merged

- name: Configure LDAP authentication
  opengear.ng.auth:
    config:
      mode: ldap
      policy: remotedownlocal
      timeout: 10
      ldapBaseDN: dc=example,dc=com
      ldapBindDN: cn=admin,dc=example,dc=com
      ldapBindPassword: "{{ ldap_bind_password }}"
      ldapUsernameAttribute: uid
      ldapGroupMembershipAttribute: memberOf
      ldapIgnoreReferrals: false
      ldapSslMode: ldaps_preferred
      ldapAuthenticationServers:
        - hostname: ldap.example.com
          port: 389
        - hostname: ldap2.example.com
          port: 389
    state: replaced

- name: Configure RADIUS authentication
  opengear.ng.auth:
    config:
      mode: radius
      policy: remotedownlocal
      timeout: 10
      radiusMethod: pap
      radiusPassword: "{{ radius_secret }}"
      radiusAccountingEnabled: true
      radiusRequireMessageAuthenticator: false
      radiusAuthenticationServers:
        - hostname: radius.example.com
          port: 1812
      radiusAccountingServers:
        - hostname: radius.example.com
          port: 1813
    state: replaced

- name: Configure TACACS+ authentication
  opengear.ng.auth:
    config:
      mode: tacacs
      policy: remotedownlocal
      timeout: 10
      tacacsMethod: pap
      tacacsService: raccess
      tacacsPassword: "{{ tacacs_secret }}"
      tacacsAccountingEnabled: true
      tacacsAuthenticationServers:
        - hostname: tacacs.example.com
          port: 49
    state: replaced

- name: Preview LDAP config change without applying (check mode)
  opengear.ng.auth:
    config:
      mode: ldap
      ldapBaseDN: dc=example,dc=com
      ldapUsernameAttribute: uid
      ldapAuthenticationServers:
        - hostname: ldap.example.com
          port: 389
    state: merged
  check_mode: true
  diff: true
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
diff:
  description: |
    The expected configuration change. Sensitive fields are omitted.
    This reflects the commands generated, not the actual device state.
  returned: when changed and diff mode is enabled
  type: dict
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
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

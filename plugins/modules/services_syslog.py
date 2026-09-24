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
module: services_syslog
version_added: '0.1.0'
short_description: Manages remote syslog server configuration on Opengear devices
description:
  - Manages the collection of remote syslog servers Opengear devices forward
    log messages to.
  - Each record's identity is the C(address)/C(port)/C(protocol) combination
    matching the the multi_field_identifier used by ogcli. Specify all three for
    reliable idempotent management.
author:
  - Opengear (@opengear)
options:
  config:
    description: The list of remote syslog servers.
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description: The device-assigned unique identifier for this syslog server. Read-only.
      multi_field_identifier:
        type: str
        description: A device-generated string combining address, port and protocol. Read-only.
      address:
        type: str
        description: The IP address or hostname of the syslog server.
        required: true
      port:
        type: int
        description: The port the syslog server is listening on. Defaults to 514 for UDP, 601 for TCP.
      protocol:
        type: str
        choices: [TCP, UDP]
        description: The protocol used to communicate with the syslog server.
      description:
        type: str
        description: A description of the syslog server for informational purposes only.
      port_logging_enabled:
        type: bool
        description: Enable sending of serial port data logs to this remote syslog server.
      min_severity:
        type: str
        choices: [emergency, alert, critical, error, warning, notice, info, debug]
        description: The minimum severity of messages sent to this remote syslog server.
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
- name: Add a remote syslog server
  opengear.ng.services_syslog:
    config:
      - address: syslog.example.com
        port: 514
        protocol: UDP
        min_severity: warning
        description: Central syslog server
    state: merged

- name: Replace all remote syslog servers with this single one
  opengear.ng.services_syslog:
    config:
      - address: syslog.example.com
        port: 514
        protocol: UDP
        min_severity: warning
    state: overridden

- name: Remove a remote syslog server
  opengear.ng.services_syslog:
    config:
      - address: syslog.example.com
        port: 514
        protocol: UDP
    state: deleted

- name: Gather services_syslog facts
  opengear.ng.facts:
    gather_network_resources:
      - services_syslog
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.services_syslog import ServicesSyslogArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.services_syslog import ServicesSyslog


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=ServicesSyslogArgs.argument_spec,
                           supports_check_mode=True)

    result = ServicesSyslog(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

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
module: system_config
version_added: '0.1.0'
short_description: Manages general system settings on Opengear devices
description:
  - Manages general system settings on Opengear devices such as the banner,
    hostname, SSH port, session timeouts and admin information.
  - The system time and timezone, SSH authorized keys and appliance reboots are
    managed by the dedicated M(opengear.ng.system_time),
    M(opengear.ng.system_authorized_keys) and M(opengear.ng.system_reboot) modules.
author:
  - Opengear (@opengear)
options:
  config:
    description: Manage configuration of general system settings on Opengear devices
    type: dict
    suboptions:
      admin_info:
        type: dict
        description: Update the Operations Manager appliance system information
        suboptions:
          hostname:
            type: str
            description: hostname or address
          contact:
            type: str
            description: contact info
          location:
            type: str
            description: location
      banner:
        type: str
        description: Update the Operations Manager appliance banner text.
      cellular_logging:
        type: dict
        description: >
          Cellular logging provides the ability to capture the RRC connection messages from the cellular module.
          This entity allows configuration of cellular logging and is only to be used during compliance testing.
        suboptions:
          enabled:
            type: bool
            description: Enable cellular logging on the device. This puts the system in Diagnostic Mode.
          filter:
            type: str
            description: The name of a binary filter to be provided to the Sierra Wireless utility.
          device:
            type: str
            description: The path to the cellular modem QCDM device.
      cell_reliability_test:
        type: dict
        description: >
          Update configuration items related to running the cell reliability test.
          This allows the user to enable and disable the test, change how frequently it executes, configure the URL
          to use in the test and configure the alert threshold for signal strength.
        suboptions:
          enabled:
            type: bool
            description: Enable or disable the cell reliability test.
          period:
            type: int
            description: The time in seconds between cell reliability test runs.
          test_url:
            type: list
            elements: str
            description: The URLs to perform the cell reliability test against.
          signal_strength_threshold:
            type: dict
            description: The lower and upper threshold values for acceptable cellular signal strength.
            suboptions:
              lower:
                type: int
                description: The lower threshold percentage value for acceptable signal strength.
              upper:
                type: int
                description: The upper threshold percentage value for acceptable signal strength.
      fips:
        type: dict
        description: Configure the Opengear device for FIPS compliance.
        suboptions:
          enabled:
            type: bool
            description: Set whether the OpenSSL package only uses FIPS 140-2 compliant cryptographic modules.
      session_timeout:
        type: dict
        description: Configure Opengear appliance session timeouts.
        suboptions:
          cli_timeout:
            type: int
            description: |
              The timeout (in minutes) for local console, web terminal, and ssh sessions.
              Maximum value is 1440.
              Set this to 0 to disable the timeout.
          webui_timeout:
            type: int
            description: |
              The timeout (in minutes) for web UI and REST API sessions.
              Maximum value is 1440.
          serial_port_timeout:
            type: int
            description: |
              The timeout (in minutes) for serial port sessions.
              Maximum value is 1440.
      ssh_port:
        type: int
        description: |
          Direct SSH links on the serial ports page will use this port number.
          Set this option if you have configured SSH to be reachable on a non-standard port.
  state:
    description:
    - The state of the configuration after module completion.
    - C(merged) and C(replaced) both update only the settings provided; unspecified
      settings are left untouched (this resource has no items to remove).
    type: str
    choices:
    - merged
    - replaced
    - gathered
    - rendered
    default: merged
"""

EXAMPLES = """
- name: Configure system information
  opengear.ng.system_config:
    config:
      banner: "Authorized access only"
      ssh_port: 22
      session_timeout:
        cli_timeout: 30
        serial_port_timeout: 30
        webui_timeout: 30
    state: merged

- name: Configure admin info
  opengear.ng.system_config:
    config:
      admin_info:
        hostname: om-device-01
        contact: netops@example.com
        location: Server Room A, Rack 3
    state: merged

- name: Gather system facts
  opengear.ng.facts:
    gather_network_resources:
      - system_config
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
from ansible_collections.opengear.ng.plugins.module_utils.argspec.system_config import SystemArgs
from ansible_collections.opengear.ng.plugins.module_utils.config.system_config import SystemConfig


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=SystemArgs.argument_spec,
                           supports_check_mode=True)

    result = SystemConfig(module).execute_module()
    for warning in result.pop('warnings', []):
        module.warn(warning)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

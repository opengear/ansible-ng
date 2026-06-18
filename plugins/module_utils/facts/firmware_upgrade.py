# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.opengear.ng.plugins.module_utils.argspec.firmware_upgrade import FirmwareUpgradeArgs


class FirmwareUpgradeFacts(object):
    """
    Retrieves firmware version and upgrade status facts from Opengear devices.
    """

    def __init__(self, module):
        self._module = module
        self.argument_spec = FirmwareUpgradeArgs.argument_spec

    def get_version(self, connection):
        return connection.get(None, 'system/version')['system_version']

    def get_upgrade_status(self, connection):
        return connection.get(None, 'system/firmware_upgrade_status')['system_firmware_upgrade_status']

    def populate_facts(self, connection, ansible_facts, data=None):
        if not data:
            version = self.get_version(connection)
            status = self.get_upgrade_status(connection)
            data = {
                'current_version': version['firmware_version'],
                'upgrade_status': status if status.get('state') else None,
            }

        ansible_facts['ansible_network_resources'].pop('firmware_upgrade', None)
        facts = {}
        if data:
            facts['firmware_upgrade'] = data
        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

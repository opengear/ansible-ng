# -*- coding: utf-8 -*-
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible_collections.opengear.ng.tests.unit.compat.mock import patch
from ansible_collections.opengear.ng.plugins.modules import services_config
from ansible_collections.opengear.ng.tests.unit.modules.utils import set_module_args
from .module_test_base import TestModuleBase, load_fixture


class TestServicesConfigModule(TestModuleBase):

    module = services_config

    def setUp(self):
        super(TestServicesConfigModule, self).setUp()
        self.maxDiff = None

        # Mock the per-field device fetch used to build the current settings.
        self.mock_get_device_data = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "facts.services_config.ServicesConfigFacts.get_device_data"
        )
        self.get_device_data = self.mock_get_device_data.start()

        self.mock_connection = patch(
            "ansible_collections.opengear.ng.plugins.module_utils."
            "config.base.Connection"
        )
        self.connection = self.mock_connection.start()

    def tearDown(self):
        super(TestServicesConfigModule, self).tearDown()
        self.mock_get_device_data.stop()
        self.mock_connection.stop()

    def load_fixtures(self, commands=None):
        self.get_device_data.return_value = load_fixture("services_config.cfg")

    # --- merged ---
    def test_merged_change_single_field_dict(self):
        """A single-field dict setting emits a single PUT for that endpoint"""
        set_module_args({
            'config': {'web': {'allow_remote_access': False}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/web',
                'data': {'web': {'allow_remote_access': False}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_idempotent(self):
        """Merging a value already present produces no commands"""
        set_module_args({
            'config': {
                'web': {'allow_remote_access': True},
                'perifrouted': {'enabled': False},
            },
            'state': 'merged',
        })

        self.execute_module(changed=False, commands=[])

    def test_merged_multiple_endpoints(self):
        """Multiple changed settings map to one PUT per endpoint"""
        set_module_args({
            'config': {
                'perifrouted': {'enabled': True},
                'tftp': {'enabled': True},
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/perifrouted',
                'data': {'perifrouted': {'enabled': True}},
                'method': 'PUT',
            },
            {
                'path': 'services/tftp',
                'data': {'tftp': {'enabled': True, 'path': '/mnt/nvram/srv'}},
                'method': 'PUT',
            },
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(
            sorted(result['commands'], key=lambda c: c['path']),
            sorted(commands, key=lambda c: c['path']),
        )

    def test_merged_brute_force_protection(self):
        """Enabling brute force protection emits a PUT with the full dict"""
        set_module_args({
            'config': {
                'brute_force_protection': {
                    'ssh_enabled': True,
                    'https_enabled': True,
                    'max_retry': 3,
                    'ban_time': 300,
                    'find_time': 5,
                },
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/brute_force_protection',
                'data': {'brute_force_protection': {
                    'ssh_enabled': True,
                    'https_enabled': True,
                    'max_retry': 3,
                    'ban_time': 300,
                    'find_time': 5,
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_ssh_partial(self):
        """A partial ssh dict is merged onto the device's current values and
        pushed as a complete object"""
        set_module_args({
            'config': {'ssh': {'maxstartups_full': 200}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/ssh',
                'data': {'ssh': {
                    'ssh_url_delimiter': '+',
                    'maxstartups_start': 10,
                    'maxstartups_rate': 30,
                    'maxstartups_full': 200,
                    'unauthenticated_serial_port_access': False,
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_https_certificate(self):
        """A single-field change to https_certificate is merged onto the device's current values"""
        set_module_args({
            'config': {'https_certificate': {'cert': 'NEW-CERT'}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/https/certificate',
                'data': {'https_certificate': {'cert': 'NEW-CERT'}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_lldp(self):
        """A partial lldp dict is merged onto the device's current values and
        pushed as a complete object"""
        set_module_args({
            'config': {'lldp': {'description': 'new description'}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/lldp',
                'data': {'lldp': {
                    'enabled': True,
                    'description': 'new description',
                    'platform': 'platform 1',
                    'portid_subtype': 'macaddress',
                    'physifs': ['net1', 'net2'],
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_snmpd(self):
        """A partial snmpd dict is merged onto the device's current values and
        pushed as a complete object"""
        set_module_args({
            'config': {'snmpd': {'port': 1161}},
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/snmpd',
                'data': {'snmpd': {
                    'enabled': False,
                    'port': 1161,
                    'protocol': 'UDP',
                    'enable_legacy_versions': False,
                    'rocommunity': 'public',
                    'rwcommunity': 'private',
                    'enable_secure_snmp': False,
                    'security_level': 'priv',
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_routing_ospfd_interfaces_updates_by_name_keeps_others(self):
        """merged matches routing.ospfd.interfaces by 'name', field-merging a matched
        entry (preserving fields not provided), keeping unlisted entries, and adding
        a new entry as given (name/non_broadcast/passive required for a new entry)"""
        set_module_args({
            'config': {
                'routing': {
                    'ospfd': {
                        'interfaces': [
                            {'name': 'net1', 'cost': 15},
                            {'name': 'net3', 'cost': 30, 'non_broadcast': False, 'passive': False},
                        ],
                    },
                },
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/routing',
                'data': {'routing': {
                    'bgpd': {'enabled': False},
                    'isisd': {'enabled': False},
                    'ripd': {'enabled': False},
                    'ospfd': {
                        'enabled': True,
                        'router_id': '1.1.1.1',
                        'redistribute_connected': False,
                        'redistribute_static': False,
                        'redistribute_kernel': False,
                        'interfaces': [
                            {'name': 'net1', 'cost': 15, 'non_broadcast': True, 'passive': False},
                            {'name': 'net2', 'cost': 20, 'non_broadcast': False, 'passive': False},
                            {'name': 'net3', 'cost': 30, 'non_broadcast': False, 'passive': False},
                        ],
                        'neighbors': [{'address': '10.0.0.1'}],
                        'networks': [{'address_with_mask': '10.0.0.0/24', 'area': '0.0.0.0'}],
                    },
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_merged_ntp_servers_updates_by_value_keeps_others(self):
        """merged matches ntp.servers by 'value', updating in place and keeping unlisted entries"""
        set_module_args({
            'config': {
                'ntp': {
                    'servers': [
                        {'value': '1.pool.ntp.org', 'key': {
                            'value': 'secret', 'index': 1, 'format': 'ASCII', 'algorithm': 'MD5',
                        }},
                        {'value': '2.pool.ntp.org'},
                    ],
                },
            },
            'state': 'merged',
        })

        commands = [
            {
                'path': 'services/ntp',
                'data': {'ntp': {
                    'enabled': True,
                    'servers': [
                        {'value': '0.pool.ntp.org'},
                        {'value': '1.pool.ntp.org', 'key': {
                            'value': 'secret', 'index': 1, 'format': 'ASCII', 'algorithm': 'MD5',
                        }},
                        {'value': '2.pool.ntp.org'},
                    ],
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- replaced ---
    def test_replaced_behaves_like_merged(self):
        """replaced on a singleton only touches provided fields"""
        set_module_args({
            'config': {'perifrouted': {'enabled': True}},
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'services/perifrouted',
                'data': {'perifrouted': {'enabled': True}},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_replaced_routing_ospfd_neighbors_drops_unlisted(self):
        """replaced sends routing.ospfd.neighbors as the complete list, dropping unlisted entries"""
        set_module_args({
            'config': {'routing': {'ospfd': {'neighbors': [{'address': '10.0.0.2'}]}}},
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'services/routing',
                'data': {'routing': {
                    'bgpd': {'enabled': False},
                    'isisd': {'enabled': False},
                    'ripd': {'enabled': False},
                    'ospfd': {
                        'enabled': True,
                        'router_id': '1.1.1.1',
                        'redistribute_connected': False,
                        'redistribute_static': False,
                        'redistribute_kernel': False,
                        'interfaces': [
                            {'name': 'net1', 'cost': 10, 'non_broadcast': True, 'passive': False},
                            {'name': 'net2', 'cost': 20, 'non_broadcast': False, 'passive': False},
                        ],
                        'neighbors': [{'address': '10.0.0.2'}],
                        'networks': [{'address_with_mask': '10.0.0.0/24', 'area': '0.0.0.0'}],
                    },
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    def test_replaced_ntp_servers_drops_unlisted(self):
        """replaced sends ntp.servers as the complete list, dropping unlisted entries"""
        set_module_args({
            'config': {'ntp': {'servers': [{'value': '2.pool.ntp.org'}]}},
            'state': 'replaced',
        })

        commands = [
            {
                'path': 'services/ntp',
                'data': {'ntp': {
                    'enabled': True,
                    'servers': [{'value': '2.pool.ntp.org'}],
                }},
                'method': 'PUT',
            }
        ]
        self.execute_module(changed=True, commands=commands)

    # --- gathered ---
    def test_gathered(self):
        """gathered returns the current settings as unwrapped config"""
        set_module_args({'state': 'gathered'})

        result = self.execute_module(changed=False)

        gathered = result['gathered']
        self.assertEqual(gathered['web']['allow_remote_access'], True)
        self.assertEqual(gathered['ssh']['maxstartups_full'], 100)
        self.assertEqual(gathered['ntp']['enabled'], True)
        self.assertEqual(len(gathered['ntp']['servers']), 2)
        # syslog/snmp_alert_managers are managed by their own dedicated modules
        self.assertNotIn('syslog', gathered)
        self.assertNotIn('snmp_alert_managers', gathered)

    # --- rendered ---
    def test_rendered(self):
        """rendered returns the commands without contacting the device"""
        set_module_args({
            'config': {'perifrouted': {'enabled': True}},
            'state': 'rendered',
        })

        result = self.execute_module(changed=False)
        self.assertEqual(
            result['rendered'],
            [
                {
                    'path': 'services/perifrouted',
                    'data': {'perifrouted': {'enabled': True}},
                    'method': 'PUT',
                }
            ],
        )

    # --- diff mode ---

    def test_diff_mode_when_changed(self):
        """diff key is present when _ansible_diff is set and a change is made"""
        set_module_args({
            '_ansible_diff': True,
            'config': {'perifrouted': {'enabled': True}},
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertIn('perifrouted', before)
        self.assertIn('perifrouted', after)

    def test_no_diff_when_not_requested(self):
        """diff key is absent when _ansible_diff is not set"""
        set_module_args({
            'config': {'perifrouted': {'enabled': True}},
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.assertNotIn('diff', result)

    def test_no_diff_when_idempotent(self):
        """diff key is absent when nothing changed"""
        set_module_args({
            '_ansible_diff': True,
            'config': {'perifrouted': {'enabled': False}},
            'state': 'merged',
        })
        result = self.execute_module(changed=False)
        self.assertNotIn('diff', result)

    def test_check_mode_with_diff_shows_simulated_change(self):
        """Check mode combined with diff mode must simulate expected
        device changes. Should be different to before facts."""
        set_module_args({
            '_ansible_check_mode': True,
            '_ansible_diff': True,
            'config': {'perifrouted': {'enabled': True}},
            'state': 'merged',
        })
        result = self.execute_module(changed=True)
        self.connection.return_value.send_request.assert_not_called()
        self.assertIn('diff', result)
        before = json.loads(result['diff']['before'])
        after = json.loads(result['diff']['after'])
        self.assertFalse(before['perifrouted']['enabled'])
        self.assertTrue(after['perifrouted']['enabled'])

# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class PhysifsArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the physifs module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "elements": "dict",
            "options": {
                "bond_setting": {
                    "options": {
                        "mode": {"type": "str"},
                        "poll_interval": {"type": "int"},
                        "primary_slave": {"type": "str"},
                    },
                    "type": "dict",
                },
                "bridge_setting": {
                    "options": {
                        "primary_slave": {"type": "str"},
                        "stp_enabled": {"type": "bool"},
                    },
                    "type": "dict",
                },
                "cellular_setting": {
                    "options": {
                        "active_sim": {"type": "int"},
                        "id": {"type": "str"},
                        "sim_failback_disconnect_mode": {"type": "str"},
                        "sim_failback_policy": {"type": "str"},
                        "sim_failover_disconnect_mode": {"type": "str"},
                        "sim_failover_policy": {"type": "str"},
                        "sims": {
                            "elements": "dict",
                            "options": {
                                "apn": {"type": "str"},
                                "fail_probe_address": {"type": "str"},
                                "fail_probe_count": {"type": "int"},
                                "fail_probe_interval": {"type": "int"},
                                "fail_probe_threshold": {"type": "int"},
                                "failback_delay": {"type": "int"},
                                "id": {"type": "str"},
                                "iptype": {"type": "str"},
                                "password": {"type": "str", "no_log": True},
                                "slot": {"type": "int"},
                                "username": {"type": "str"},
                            },
                            "type": "list",
                        },
                    },
                    "type": "dict",
                },
                "description": {"type": "str"},
                "enabled": {"type": "bool"},
                "ethernet_setting": {
                    "options": {"link_speed": {"type": "str"}},
                    "type": "dict",
                },
                "id": {"type": "str"},
                "media": {"type": "str"},
                "mtu": {"type": "int"},
                "name": {"type": "str"},
                "slaves": {"elements": "str", "type": "list"},
                "vlan_setting": {
                    "options": {
                        "parent_physif": {"type": "str"},
                        "vlan_id": {"type": "int"},
                    },
                    "type": "dict",
                },
            },
            "type": "list",
        },
        "state": {
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
            ],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301

# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class SystemArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the system module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "options": {
                "admin_info": {
                    "options": {
                        "contact": {"type": "str"},
                        "hostname": {"type": "str"},
                        "location": {"type": "str"},
                    },
                    "type": "dict",
                },
                "banner": {"type": "str"},
                "cell_reliability_test": {
                    "options": {
                        "enabled": {"type": "bool"},
                        "period": {"type": "int"},
                        "signal_strength_threshold": {
                            "options": {
                                "lower": {"type": "int"},
                                "upper": {"type": "int"},
                            },
                            "type": "dict",
                        },
                        "test_url": {"elements": "str", "type": "list"},
                    },
                    "type": "dict",
                },
                "cli_session_timeout": {"type": "int"},
                "hostname": {"type": "str"},
                "reboot": {"type": "bool"},
                "ssh_port": {"type": "int"},
                "system_authorized_keys": {
                    "elements": "dict",
                    "options": {
                        "id": {"type": "str"},
                        "key": {"type": "str", "no_log": True},
                        "username": {"type": "str"},
                        "multi_field_identifier": {"type": "str"},
                    },
                    "type": "list",
                    "no_log": True,
                },
                "time": {"type": "str"},
                "timezone": {"type": "str"},
                "webui_session_timeout": {"type": "int"},
            },
            "type": "dict",
        },
        "state": {
            "choices": ["merged", "overridden", "deleted", "gathered", "rendered"],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301

# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ConnsArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the conns module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "elements": "dict",
            "options": {
                "id": {"type": "str"},
                "ipv4_static_settings": {
                    "options": {
                        "address": {"type": "str"},
                        "broadcast": {"type": "str"},
                        "dns1": {"type": "str"},
                        "dns2": {"type": "str"},
                        "gateway": {"type": "str"},
                        "netmask": {"type": "str"},
                    },
                    "type": "dict",
                },
                "ipv6_static_settings": {
                    "options": {
                        "address": {"type": "str"},
                        "dns1": {"type": "str"},
                        "dns2": {"type": "str"},
                        "gateway": {"type": "str"},
                        "prefix_length": {"type": "str"},
                    },
                    "type": "dict",
                },
                "mode": {"type": "str"},
                "name": {"type": "str"},
                "physif": {"type": "str"},
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

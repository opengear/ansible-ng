# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class AuthArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the auth module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "options": {
                "ldapAuthenticationServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "ldapBaseDN": {"type": "str"},
                "ldapBindDN": {"type": "str"},
                "ldapBindPassword": {"type": "str", "no_log": True},
                "ldapGroupMembershipAttribute": {"type": "str"},
                "ldapIgnoreReferals": {"type": "bool"},
                "ldapUsernameAttribute": {"type": "str"},
                "mode": {"type": "str"},
                "policy": {"type": "str"},
                "radiusAccountingServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "radiusAuthenticationServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "radiusPassword": {"type": "str", "no_log": True},
                "tacacsAuthenticationServers": {
                    "elements": "dict",
                    "options": {
                        "hostname": {"type": "str"},
                        "id": {"type": "str"},
                        "port": {"type": "int"},
                    },
                    "type": "list",
                },
                "tacacsMethod": {"type": "str"},
                "tacacsPassword": {"type": "str", "no_log": True},
                "tacacsService": {"type": "str"},
            },
            "type": "dict",
        },
        "state": {
            "choices": ["merged", "replaced", "overridden", "gathered", "rendered"],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301

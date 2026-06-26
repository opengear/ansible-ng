# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class UsersArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the users module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "elements": "dict",
            "options": {
                "description": {"type": "str"},
                "enabled": {"type": "bool"},
                "groups": {"elements": "str", "type": "list"},
                "groupNames": {"elements": "str", "type": "list"},
                "hashed_password": {"type": "str", "no_log": True},
                "id": {"type": "str"},
                "no_password": {"type": "bool"},
                "password": {"type": "str", "no_log": True},
                "ssh_password_enabled": {"type": "bool"},
                "username": {"type": "str"},
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

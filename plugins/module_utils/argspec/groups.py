# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class GroupsArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the groups module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "elements": "dict",
            "options": {
                "description": {"type": "str"},
                "enabled": {"type": "bool"},
                "groupname": {"type": "str"},
                "id": {"type": "str"},
                "access_rights": {"elements": "str", "type": "list"},
                "members": {"elements": "str", "type": "list"},
                "mode": {"type": "str"},
                "ports": {"elements": "str", "type": "list"},
                "role": {"type": "str"},
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

# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class UserAuthorizedKeysArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the user_authorized_keys module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "username": {
                    "type": "str",
                    "required": True,
                },
                "keys": {
                    "type": "list",
                    "elements": "str",
                    'no_log': False,
                },
            },
        },
        "state": {
            "type": "str",
            "default": "merged",
            "choices": [
                "merged",
                "replaced",
                "deleted",
                "gathered",
            ],
        },
    }

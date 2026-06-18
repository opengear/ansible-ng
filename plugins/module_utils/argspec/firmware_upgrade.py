# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class FirmwareUpgradeArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the firmware_upgrade module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "dict",
            "options": {
                "version": {"type": "str"},
                "firmware_image": {"type": "str"},
                "ignore_version": {"type": "bool", "default": False},
                "erase_config": {"type": "bool", "default": False},
            },
        },
        "state": {
            "choices": [
                "merged",
                "gathered",
            ],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301

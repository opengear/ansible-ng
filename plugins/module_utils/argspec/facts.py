# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class FactsArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the facts module.
    """

    def __init__(self, **kwargs):
        pass

    choices = [
        'all',
        'auth',
        'conns',
        'failover',
        'firmware_upgrade',
        'groups',
        'physifs',
        'ports',
        'pdu',
        'services',
        'static_routes',
        'system',
        'users'
    ]

    argument_spec = {
        "gather_subset": dict(default=["all"], type="list", elements="str"),
        "gather_network_resources": dict(choices=choices, type="list", elements="str"),
    }

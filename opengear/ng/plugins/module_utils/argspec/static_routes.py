# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class StaticRoutesArgs(object):  # pylint: disable=R0903
    """
    Argument specification for the static_routes module.
    """

    def __init__(self, **kwargs):
        pass

    argument_spec = {'config': {'elements': 'dict',
                                'options': {'destination_address': {'type': 'str'},
                                            'destination_netmask': {'type': 'int'},
                                            'gateway_address': {'type': 'str'},
                                            'id': {'type': 'str'},
                                            'description': {'type': 'str'},
                                            'interface': {'type': 'str'},
                                            'metric': {'type': 'int'}},
                                'type': 'list'},
                     'state': {'choices': ['merged',
                                           'replaced',
                                           'overridden',
                                           'deleted',
                                           'gathered',
                                           'rendered'],
                               'default': 'merged',
                               'type': 'str'}}  # pylint: disable=C0301

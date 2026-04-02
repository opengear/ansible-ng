# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class BannerArgs(object):

    argument_spec = {
        'config': {
            'type': 'dict',
            'options': {
                'banner': {'type': 'str'},
            },
        },
        'state': {
            'type': 'str',
            'choices': ['merged', 'replaced', 'overridden', 'deleted', 'gathered', 'rendered', 'parsed'],
            'default': 'merged',
        },
    }

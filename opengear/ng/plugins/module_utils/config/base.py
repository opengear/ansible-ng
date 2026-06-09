# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible.module_utils.connection import Connection

__metaclass__ = type


class ConfigBase(object):
    """
    Base class for Opengear resource configuration modules. Provides common
    state handling, connection management, and action state definitions.
    """

    ACTION_STATES = ['merged', 'replaced', 'overridden', 'deleted']

    def __init__(self, module):
        self._module = module
        self._connection = module.params.get('_connection') if hasattr(module, 'params') else None
        # Set connection via the module's socket path
        if not self._connection:
            try:
                self._connection = Connection(self._module._socket_path)
            except Exception:
                pass

    @property
    def state(self):
        return self._module.params.get('state')

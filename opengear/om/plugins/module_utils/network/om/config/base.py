# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ConfigBase(object):
    """
    Base class for resource module config classes.
    """

    ACTION_STATES = ['merged', 'replaced', 'overridden', 'deleted']

    def __init__(self, module):
        self._module = module
        self._connection = module.params.get('_connection') if hasattr(module, 'params') else None
        # Set connection via the module's socket path
        if not self._connection:
            try:
                from ansible.module_utils.connection import Connection
                self._connection = Connection(self._module._socket_path)
            except Exception:
                pass

    @property
    def state(self):
        return self._module.params.get('state')

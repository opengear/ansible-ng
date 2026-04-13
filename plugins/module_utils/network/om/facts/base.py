# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type


class FactsBase(object):
    """
    Base class for facts modules.
    """

    def __init__(self, module):
        self._module = module
        self._warnings = []
        self.ansible_facts = {'ansible_network_resources': {}, 'ansible_network_legacy_facts': {}}
        try:
            from ansible.module_utils.connection import Connection
            self._connection = Connection(self._module._socket_path)
        except Exception:
            self._connection = None

    def get_network_resources_facts(self, fact_resource_subsets, resource_facts_type, data=None):
        """Gather facts for each requested resource type."""
        if not resource_facts_type:
            return
        for resource in resource_facts_type:
            if resource in fact_resource_subsets:
                facts_cls = fact_resource_subsets[resource]
                instance = facts_cls(self._module)
                instance.populate_facts(self._connection, self.ansible_facts, data)

    def get_network_legacy_facts(self, fact_legacy_subsets, legacy_facts_type):
        """Gather legacy facts (no-op for collections with no legacy facts)."""
        pass

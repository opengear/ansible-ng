# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.opengear.ng.plugins.module_utils.argspec.ports import PortsArgs
from ansible_collections.opengear.ng.plugins.module_utils.utils import utils


class PortsFacts(object):
    """
    Retrieves and parses ports configuration facts from Opengear devices.
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = PortsArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_device_data(self, connection):
        data = {}
        for option in self.generated_spec.keys():
            path = 'ports'
            if option == 'auto_discover':
                path += '/' + option + '/schedule'
                value = {'auto_discover': {'schedule': connection.get(None, path)['auto_discover_schedule']}}
                value['auto_discover']['ports'] = value['auto_discover']['schedule'].pop('ports', None)
            else:
                value = connection.get(None, path)

            data.update(value)
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for ports
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """

        if not data:
            data = self.get_device_data(connection)

        obj = {}
        if data:
            obj.update(self.render_config(self.generated_spec, data))
        ansible_facts['ansible_network_resources'].pop('ports', None)
        facts = {}
        if obj:
            params = utils.validate_config(self.argument_spec, {'config': obj})
            facts['ports'] = params['config']
        else:
            facts['ports'] = {}
        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)
        for option in config.keys():
            if option in conf:
                if isinstance(conf[option], dict):
                    config[option] = self.render_config(config[option], conf[option])
                else:
                    if isinstance(conf[option], list):
                        for suboption in conf[option]:
                            suboption.pop('available_pinouts', None)
                            suboption.pop('device', None)
                            suboption.pop('status', None)
                            if 'sessions' in suboption:
                                for session in suboption['sessions']:
                                    session.pop('port', None)
                    config[option] = conf[option]
        return utils.remove_empties(config)

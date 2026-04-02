# -*- coding: utf-8 -*-
# Copyright 2024 Opengear Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.banner.banner import BannerArgs


class BannerFacts(object):

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = BannerArgs.argument_spec

    def get_device_data(self, connection):
        if hasattr(connection, 'send_request'):
            response = connection.send_request(None, 'system/banner')
            return {'banner': response.get('system_banner', {}).get('banner', '')}
        else:
            # TODO: implement CLI retrieval
            # output = connection.get('ogcli -j get system/banner')
            # return self._parse_cli_output(output)
            raise NotImplementedError("CLI transport not yet supported for banner facts")

    def populate_facts(self, connection, ansible_facts, data=None):
        if not data:
            data = self.get_device_data(connection)

        obj = utils.remove_empties(data) if data else {}

        ansible_facts['ansible_network_resources'].pop('banner', None)
        if obj:
            params = utils.validate_config(self.argument_spec, {'config': obj})
            ansible_facts['ansible_network_resources']['banner'] = params['config']
        else:
            ansible_facts['ansible_network_resources']['banner'] = {}

        return ansible_facts

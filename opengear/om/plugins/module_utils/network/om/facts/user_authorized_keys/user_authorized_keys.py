#!/usr/bin/python
# -*- coding: utf-8 -*-

from copy import deepcopy
from ansible_collections.opengear.om.plugins.module_utils.network.om.utils import utils
from ansible_collections.opengear.om.plugins.module_utils.network.om.argspec.user_authorized_keys.user_authorized_keys import UserAuthorizedKeysArgs


class UserAuthorizedKeysFacts(object):
    """ The user_authorized_keys facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = UserAuthorizedKeysArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def get_users(self, connection):
        """ Fetch all users to build username -> user_id map """
        return connection.get(None, 'users')['users']

    def get_device_data(self, connection, user_id):
        """ Fetch authorized keys for a specific user """
        return connection.get(None, f'users/{user_id}/ssh/authorized_keys').get('authorized_keys', [])

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for user_authorized_keys

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        objs = []

        if data:
            # data passed directly (e.g. from gathered state in tests)
            objs = data
        else:
            # fetch users to get username -> id mapping
            users = self.get_users(connection)
            for user in users:
                user_id = user['id']
                username = user['username']
                raw_keys = self.get_device_data(connection, user_id)

                # preserve id and key string internally for DELETE path resolution
                # key_fingerprint is informational only, not included
                keys = [
                    {'id': k['id'], 'key': k['key']}
                    for k in raw_keys
                ]

                if keys:
                    objs.append({
                        'username': username,
                        'user_id': user_id,
                        'keys': keys,
                    })

        ansible_facts['ansible_network_resources'].pop('user_authorized_keys', None)
        facts = {}
        if objs:
            facts['user_authorized_keys'] = objs

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

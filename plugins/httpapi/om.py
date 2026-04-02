# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Opengear Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
name: om
short_description: HttpApi Plugin for Opengear OM & CM8100 devices
description:
  - This HttpApi plugin provides methods to connect to Opengear OM & CM8100
    devices over a HTTP(S)-based API.
options: {}
version_added: "1.0.2"
author:
  - Adrian Van Katwyk (@avankatwyk)
  - Matt Witmer (@mattwitt)
'''

import json

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible.plugins.httpapi import HttpApiBase


def handle_response(response):
    """Parse a JSON response body, raising ConnectionError on API errors."""
    if not response:
        return None

    raw = to_text(response.getvalue()).strip()
    if not raw:
        return None

    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ConnectionError(
            "Invalid JSON response: {0}".format(to_text(exc))
        )

    if "error" in data:
        error = data["error"][0]
        raise ConnectionError(error["text"], code=error["code"])

    return data


class HttpApi(HttpApiBase):

    def __init__(self, *args, **kwargs):
        super(HttpApi, self).__init__(*args, **kwargs)
        self._device_info = None
        self._api_path = '/api/v2/'

    def login(self, username, password):
        if not username or not password:
            raise ConnectionError("Username and password are required for login")
        data = {'username': username, 'password': password}
        response = self.send_request(data, 'sessions/', 'POST')
        try:
            token = response['session']
        except (KeyError, TypeError):
            raise ConnectionError("Login failed: no session token in response")
        self.connection._auth = {'Authorization': 'Token ' + token}

    def logout(self):
        self.send_request(None, 'sessions/self', 'DELETE')
        self.connection._auth = None

    def update_auth(self, response, response_text):
        # Token auth is set once in login(); no per-request cookie handling.
        return None

    def send_request(self, data, path='', method='GET'):
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data) if data is not None else None

        separator = '&' if '?' in path else '?'
        url = self._api_path + path + separator + 'use_names=true'

        _, response_content = self.connection.send(
            url,
            body,
            method=method,
            headers=headers,
        )
        return handle_response(response_content)


    def get_device_info(self):
        if self._device_info:
            return self._device_info

        device_info = {}
        version_response = self.send_request(None, 'system/version')['system_version']
        device_info['firmware_version'] = version_response['firmware_version']
        device_info['rest_api_version'] = version_response['rest_api_version']

        for endpoint in ('hostname', 'serial_number', 'model_name'):
            resp = self.send_request(None, 'system/' + endpoint)
            device_info[endpoint] = resp['system_' + endpoint][endpoint]

        self._device_info = device_info
        return self._device_info

    def get_capabilities(self):
        result = {
            "network_api": "httpapi",
            "device_info": self.get_device_info(),
        }
        return json.dumps(result)

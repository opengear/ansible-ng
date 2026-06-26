# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, Opengear Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
name: http_api
short_description: HttpApi Plugin for Opengear devices
description:
  - This HttpApi plugin provides methods to connect to Opengear devices over a HTTP-based API.
options: {}
version_added: "1.0.0"
'''

import json
import os
import uuid

from ansible.module_utils.connection import ConnectionError
from ansible.plugins.httpapi import HttpApiBase


def handle_response(response):
    if response:
        content = response.getvalue()
        if not content:
            return {}
        try:
            handled_response = json.loads(content)
        except ValueError:
            return {}
        if "error" in handled_response:
            error = handled_response["error"][0]
            raise ConnectionError(error["text"], code=error["code"])
        return handled_response
    return {}


class HttpApi(HttpApiBase):
    """
    HttpApi plugin for Opengear devices. Handles authentication, request
    routing, and response parsing for the Opengear REST API.
    """
    def __init__(self, *args, **kwargs):
        super(HttpApi, self).__init__(*args, **kwargs)
        self._device_info = None
        self.path = '/api/v2/'

    def login(self, username, password):
        login_path = 'sessions/'
        data = {'username': username, 'password': password}
        response = self.send_request(data, login_path, 'POST')
        self.connection._auth = {'Authorization': 'Token ' + response['session']}

    def get(self, command, path, query_params):
        return self.send_request(data=command, path=path, query_params=query_params)

    def send_request(self, data, path, method='GET', query_params=None):
        headers = {'Content-Type': 'application/json'}
        if query_params:
            query_string = '&'.join(f'{k}={v}' for k, v in query_params.items())
            path = f'{path}?{query_string}'
        response, response_content = self.connection.send(self.path + path, json.dumps(data),
                                                          method=method, headers=headers)
        return handle_response(response_content)

    def send_multipart_request(self, path, file_path=None, additional_fields=None):
        boundary = f'----FormBoundary{uuid.uuid4().hex}'
        parts = b''

        # Add additional fields first
        if additional_fields:
            for key, value in additional_fields.items():
                if value:
                    parts += (
                        f'--{boundary}\r\n'
                        f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
                        f'{value}\r\n'
                    ).encode()

        # Add file part only if file_path provided
        if file_path:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            filename = os.path.basename(file_path)
            parts += (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                f'Content-Type: application/octet-stream\r\n\r\n'
            ).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()
        else:
            parts += f'--{boundary}--\r\n'.encode()

        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(parts)),
        }

        response, response_content = self.connection.send(
            self.path + path, parts, method='POST', headers=headers
        )
        return handle_response(response_content)

    def logout(self):
        logout_path = 'sessions/self'
        self.send_request(None, logout_path, method='DELETE')
        self.connection._auth = None

    def get_device_info(self):
        if self._device_info:
            return self._device_info

        device_info = {}
        version_reply = self.send_request(None, 'system/version')['system_version']

        device_info['firmware_version'] = version_reply['firmware_version']
        device_info['rest_api_version'] = version_reply['rest_api_version']

        endpoints = ['hostname', 'serial_number', 'model_name']
        for endpoint in endpoints:
            device_info[endpoint] = self.send_request(None, 'system/' + endpoint)['system_' + endpoint][endpoint]
        self._device_info = device_info
        return self._device_info

    def get_capabilities(self):
        result = {'device_info': self.get_device_info()}
        return json.dumps(result)

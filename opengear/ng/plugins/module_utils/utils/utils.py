# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# Copyright 2026 Opengear
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

structure = """{
  "system": {
    "hostname": ["system_hostname", "hostname"],
    "banner": ["system_banner", "banner"],
    "webui_session_timeout": ["system_webui_session_timeout", "timeout"],
    "cli_session_timeout": ["system_cli_session_timeout", "timeout"],
    "system_authorized_keys": ["system_authorized_keys"],
    "ssh_port": ["system_ssh_port", "port"],
    "timezone": ["system_timezone", "timezone"],
    "time": ["time", "time"],
    "admin_info": ["system_admin_info"]
  }
}"""


def get_restapi_body_structure():
    return json.loads(structure)


def command_builder(data, path, instance_id=None, delete_exceptions=None, method=None):
    """
    A command builder that produces PUT, POST or DELETE commands depending on the parameters provided.
    :param method: A method that may be PUT, POST or DELETE. None by default.
    :param data: The data forming the body of the request.
    :param path: The endpoint URI path.
    :param instance_id: The id value of the instance.
    :param delete_exceptions: Any instance ids that may not be deleted.
    :return: A PUT command if id and data are provided, a DELETE command if no data is provided and provided id value
     is not an exception, a POST request if data is provided and an id value is not, or None if command isn't valid.
    """
    if method:
        return {'data': data, 'path': path, 'method': method}
    if instance_id:
        path += instance_id
        if data:
            method = 'PUT'
        elif not delete_exceptions or instance_id not in delete_exceptions:
            method = 'DELETE'
    elif data:
        method = 'POST'
    if method:
        return {'data': data, 'path': path, 'method': method}


def find_instance_id(name_id_map, name, instance):
    """
    Finds the id value of a configuration instance (user, group, conn, etc) using a given name value. If the instance
    has an id value, this will be returned. Otherwise, the name value of the instance will be used to search a
    name-id map.
    :param name_id_map: The mapping of name values to id values.
    :param name: The name key string (username, groupname, etc).
    :param instance: The configuration instance for which the id value belongs to.
    :return: An id value. If instance does not contain either an id or name value, or if the map does not contain a
    matching id value, None is returned.
    """
    instance_id = None
    if instance:
        instance_id = instance.pop('id', None)
        if instance_id and instance_id not in name_id_map.values():
            instance_id = None
        if not instance_id and name in instance and instance[name] in name_id_map:
            instance_id = name_id_map[instance[name]]
    return instance_id


def is_subset(want, have):
    if len(want) > len(have):
        return False
    for key in want.keys():
        if key not in have:
            return False
        if isinstance(want[key], list) and isinstance(have[key], list) and not set(want[key]).issubset(set(have[key])):
            return False
        if isinstance(want[key], dict) and isinstance(have[key], dict) and not is_subset(want[key], have[key]):
            return False
        if want[key] != have[key]:
            return False
    return True


def to_list(val):
    """Convert a value to a list. None returns [], scalars are wrapped."""
    if isinstance(val, list):
        return val
    elif val is None:
        return []
    else:
        return [val]


def dict_diff(base, comparable):
    """Return a dict of keys in comparable that differ from base."""
    diff = {}
    for key, value in comparable.items():
        if key not in base:
            diff[key] = value
        elif isinstance(value, dict) and isinstance(base.get(key), dict):
            nested = dict_diff(base[key], value)
            if nested:
                diff[key] = nested
        elif isinstance(value, list) and isinstance(base.get(key), list):
            # Normalise order before comparing
            if sorted(value) != sorted(base[key]):
                diff[key] = value
        elif base[key] != value:
            diff[key] = value
    return diff


def dict_merge(base, other):
    """Recursively merge other into base, returning a new dict."""
    result = base.copy()
    for key, value in other.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = dict_merge(result[key], value)
        elif isinstance(value, list) and isinstance(result.get(key), list):
            # Union: preserve existing items, append new ones
            existing = result[key]
            result[key] = existing + [item for item in value if item not in existing]
        else:
            result[key] = value
    return result


def remove_empties(cfg_dict):
    """Recursively remove keys with None, '', or {} values. Empty lists are allowed."""
    result = {}
    for key, value in cfg_dict.items():
        if isinstance(value, dict):
            nested = remove_empties(value)
            if nested:
                result[key] = nested
        elif value not in (None, '', {}):
            result[key] = value
    return result


def generate_dict(spec):
    """Generate a dict from an argspec, using default values where present."""
    result = {}
    for key, value in spec.items():
        if isinstance(value, dict):
            if 'default' in value:
                result[key] = value['default']
            elif value.get('type') == 'list':
                if 'options' in value:
                    result[key] = [generate_dict(value['options'])]
                else:
                    result[key] = []
            elif value.get('type') == 'dict':
                if 'options' in value:
                    result[key] = generate_dict(value['options'])
                else:
                    result[key] = {}
            elif value.get('type') == 'bool':
                result[key] = False
            elif value.get('type') == 'int':
                result[key] = None
            else:
                result[key] = None
        else:
            result[key] = None
    return result


def validate_config(spec, data):
    """Basic config validator - returns data as-is (validation handled by AnsibleModule)."""
    return data

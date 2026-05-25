"""
The arg spec for the om_user_authorized_keys module
"""
 
from __future__ import absolute_import, division, print_function
 
__metaclass__ = type
 
 
class UserAuthorizedKeysArgs(object):  # pylint: disable=R0903
    """The arg spec for the om_user_authorized_keys module
    """
 
    def __init__(self, **kwargs):
        pass
 
    argument_spec = {
        'config': {
            'type': 'list',
            'elements': 'dict',
            'options': {
                'username': {
                    'type': 'str',
                    'required': True,
                },
                'keys': {
                    'type': 'list',
                    'elements': 'str',
                },
            },
        },
        'state': {
            'type': 'str',
            'default': 'merged',
            'choices': [
                'merged',
                'replaced',
                'deleted',
                'gathered',
            ],
        },
    }
 
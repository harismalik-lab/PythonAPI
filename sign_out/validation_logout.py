"""
Validation parser file for the logout api calls
validates the __i (user id), __sid(session id) and session_token
"""
from flask_restful.inputs import regex

from common.common_helpers import get_request_parser

user_sign_out_parser = get_request_parser()
user_sign_out_parser.add_argument(
    '__i',
    type=int,
    required=False,
    location=['mobile', 'values', 'json'],
    help='User identity is missing.'
)
user_sign_out_parser.add_argument(
    '__sid',
    type=int,
    required=False,
    location=['mobile', 'values', 'json'],
    help='Request parameter __sid is empty.'
)
user_sign_out_parser.add_argument(
    'session_token',
    type=regex('[0-9a-zA-Z]*[-]*'),
    required=True,
    location=['mobile', 'values', 'json'],
    help='request parameter session_token is empty'
)

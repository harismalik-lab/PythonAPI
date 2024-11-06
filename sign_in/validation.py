"""
Validation for Sign in api
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import device_list, validate_email_string

user_login_in_parser = get_request_parser()
user_login_in_parser.add_argument(
    'email',
    type=validate_email_string,
    required=True,
    location=['mobile', 'json', 'values']
)
user_login_in_parser.add_argument(
    'password',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='password required'
)
user_login_in_parser.add_argument(
    'device_os',
    type=str,
    required=True,
    location=['mobile', 'json', 'values'],
    help='device_os required'
)
user_login_in_parser.add_argument(
    'issocial',
    type=int,
    required=False,
    location=['mobile', 'json', 'values'],
    default=0,
    help='Social required'
)
user_login_in_parser.add_argument(
    'device_model',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    default='',
    help='device model required'
)
user_login_in_parser.add_argument(
    'device_install_token',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device install token required'
)
user_login_in_parser.add_argument(
    'device_uid',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device uid required'
)
user_login_in_parser.add_argument(
    'facebook',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='facebook required'
)
user_login_in_parser.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values'],
    help='language required'
)
user_login_in_parser.add_argument(
    'app_version',
    type=str,
    required=False,
    default="",
    location=['mobile', 'json', 'values'],
    help='app version required'
)
user_login_in_parser.add_argument(
    'device_key',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device required'
)
user_login_in_parser.add_argument(
    'location_id',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'json', 'values'],
    help='location id required'
)
user_login_in_parser.add_argument(
    '__platform',
    type=device_list,
    location=['mobile', 'json', 'values'],
    required=True
)
user_login_in_parser.add_argument(
    'session_token',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    default=""
)

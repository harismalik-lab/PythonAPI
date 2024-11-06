"""
Validation for Sign in api
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import validate_email_string, validate_platform_for_reward

reward_user_login_in_parser = get_request_parser()
reward_user_login_in_parser.add_argument(
    'email',
    type=validate_email_string,
    required=True,
    location=['mobile', 'json', 'values']
)
reward_user_login_in_parser.add_argument(
    'password',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='password required'
)
reward_user_login_in_parser.add_argument(
    'device_os',
    type=validate_platform_for_reward,
    required=True,
    location=['mobile', 'json', 'values']
)
reward_user_login_in_parser.add_argument(
    'issocial',
    type=int,
    required=False,
    location=['mobile', 'json', 'values'],
    default=0,

    help='Social required'
)
reward_user_login_in_parser.add_argument(
    'device_model',
    type=str,
    required=True,
    location=['mobile', 'json', 'values'],
    help='device model required'
)
reward_user_login_in_parser.add_argument(
    'device_install_token',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device install token required'
)
reward_user_login_in_parser.add_argument(
    'device_uid',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device uid required'
)
reward_user_login_in_parser.add_argument(
    'facebook',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='facebook required'
)
reward_user_login_in_parser.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values'],
    help='language required'
)
reward_user_login_in_parser.add_argument(
    'app_version',
    type=str,
    required=False,
    default="",
    location=['mobile', 'json', 'values'],
    help='app version required'
)
reward_user_login_in_parser.add_argument(
    'session_token',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    default=""
)
reward_user_login_in_parser.add_argument(
    'vip_key',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

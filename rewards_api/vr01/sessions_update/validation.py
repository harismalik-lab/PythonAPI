"""
Validation for Sessions Update
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import validate_email_string, validate_platform_for_reward

rewards_user_session_update = get_request_parser()
rewards_user_session_update.add_argument(
    'vip_key',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
rewards_user_session_update.add_argument(
    'customer_id',
    type=int,
    required=False,
    location=['mobile', 'json', 'values']
)
rewards_user_session_update.add_argument(
    'device_os',
    type=validate_platform_for_reward,
    required=True,
    location=['mobile', 'json', 'values'],
    help='device_os required'
)
rewards_user_session_update.add_argument(
    'device_model',
    type=str,
    required=True,
    location=['mobile', 'json', 'values'],
    help='device model required'
)
rewards_user_session_update.add_argument(
    'device_install_token',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device install token required'
)
rewards_user_session_update.add_argument(
    'device_uid',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    help='device uid required'
)
rewards_user_session_update.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values'],
    help='language required'
)
rewards_user_session_update.add_argument(
    'app_version',
    type=str,
    required=False,
    default="",
    location=['mobile', 'json', 'values'],
    help='app version required'
)
rewards_user_session_update.add_argument(
    'session_token',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
    default=""
)

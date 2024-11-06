
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import language, boolean

user_password_reset_in_parser = get_request_parser()
user_password_reset_in_parser.add_argument(
    'language',
    required=False,
    default="en",
    type=language,
    location=['values', 'json', 'mobile']
)
user_password_reset_in_parser.add_argument(
    'email',
    type=str,
    required=False,
    location=['values', 'json', 'mobile']
)
user_password_reset_in_parser.add_argument(
    'reset_password',
    type=boolean,
    required=False,
    location=['values', 'json', 'mobile'],
    default=0
)

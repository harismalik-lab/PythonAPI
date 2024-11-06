from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import language, validate_email_string

rewards_user_password_reset_in_parser = get_request_parser()
rewards_user_password_reset_in_parser.add_argument(
    'language',
    required=False,
    default="en",
    type=language,
    location=['values', 'json', 'mobile']
)
rewards_user_password_reset_in_parser.add_argument(
    'email',
    type=validate_email_string,
    required=False,
    location=['values', 'json', 'mobile']
)

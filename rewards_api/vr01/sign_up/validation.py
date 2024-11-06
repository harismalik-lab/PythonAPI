from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import (device_list_for_sign_up, validate_email_string, validate_gender,
                                                 validate_value, language)

rewards_user_sign_up_in_parser = get_request_parser()
rewards_user_sign_up_in_parser.add_argument(
    'firstname',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'lastname',
    type=str,
    required=False,
    location=['mobile', 'values', 'json'],
)
rewards_user_sign_up_in_parser.add_argument(
    'mobile_phone',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'country_of_residence',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'email',
    type=validate_email_string,
    required=True,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'password',
    type=str,
    required=True,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'confirm_password',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'do_not_email',
    type=int,
    required=False,
    default=1,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'third_do_not_email',
    type=int,
    required=False,
    default=1,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'terms_acceptance',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json'],
    help='terms_acceptance required'
)
rewards_user_sign_up_in_parser.add_argument(
    'social_registration',
    type=int,
    required=False,
    default=0,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'session_token',
    type=validate_value,
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'facebook',
    type=validate_value,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'language',
    type=language,  # a-z
    required=False,
    default="en",
    location=['mobile', 'values', 'json'],
    help='language is empty'
)
rewards_user_sign_up_in_parser.add_argument(
    'device_os',
    type=device_list_for_sign_up,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'device_model',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'device_install_token',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'device_uid',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'app_version',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'gender',
    type=validate_gender,
    required=False,
    default="",
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'nationality',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'date_of_birth',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'device_key',
    type=validate_value,
    required=False,
    location=['mobile', 'values', 'json']
)
rewards_user_sign_up_in_parser.add_argument(
    'location_id',
    type=int,
    required=False,
    location=['mobile', 'values', 'json'],
    default=0,
    help='location id is empty'
)
rewards_user_sign_up_in_parser.add_argument(
    'affiliate_code',
    type=str,
    required=False,
    default="",
    location=['mobile', 'values', 'json'],
    help='Social required'
)
rewards_user_sign_up_in_parser.add_argument(
    'vip_key',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

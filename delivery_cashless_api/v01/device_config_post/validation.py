"""
Validation for Delivery cashless Sign in api
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import boolean

merchant_login_parser = get_request_parser()
merchant_login_parser.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'device_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'device_make',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'device_model',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'android_version',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'group_name',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login_parser.add_argument(
    'app_version',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

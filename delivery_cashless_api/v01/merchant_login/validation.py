"""
Validation for merchant
"""
from common.common_helpers import get_request_parser

merchant_login = get_request_parser()


merchant_login.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'pin',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'device_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'language',
    type=str,
    default='en',
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'device_model',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'device_token',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'device_id',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)
merchant_login.add_argument(
    'device_name',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values']
)




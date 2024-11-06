"""
Validation for Active status management for outlet api
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import boolean

device_token_parser = get_request_parser()

device_token_parser.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values']
)
device_token_parser.add_argument(
    'device_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_token_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_token_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_token_parser.add_argument(
    'device_token',
    type=str,
    required=True,
    location=['mobile', 'json', 'values'],
)
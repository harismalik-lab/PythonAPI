"""
Validation for delivery settings api
"""
from common.common_helpers import get_request_parser

delivery_settings_parser = get_request_parser()

delivery_settings_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)

delivery_settings_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)


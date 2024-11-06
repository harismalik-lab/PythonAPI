"""
Validation for get menu api
"""
from common.common_helpers import get_request_parser

get_outlet_menu_parset = get_request_parser()

get_outlet_menu_parset.add_argument(
    'outlet_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
get_outlet_menu_parset.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
get_outlet_menu_parset.add_argument(
    'language',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
get_outlet_menu_parset.add_argument(
    'device_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values'],
)

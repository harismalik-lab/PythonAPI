"""
Validation for menu item status change
"""

from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import boolean

outlet_menu_status_parser = get_request_parser()

outlet_menu_status_parser.add_argument(
    'item_id',
    type=int,
    required=True,
    location=['mobile', 'json', 'values']
)
outlet_menu_status_parser.add_argument(
    'item_status',
    type=boolean,
    required=True,
    location=['mobile', 'json', 'values']
)
outlet_menu_status_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
outlet_menu_status_parser.add_argument(
    'device_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
outlet_menu_status_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)

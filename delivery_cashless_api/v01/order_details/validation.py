"""
Validation for delivery details api
"""
from common.common_helpers import get_request_parser

order_details_parser = get_request_parser()

order_details_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
order_details_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
order_details_parser.add_argument(
    'merchant_id',
    type=int,
    required=False,
    location=['mobile', 'json', 'values']
)
order_details_parser.add_argument(
    'outlet_id',
    type=int,
    required=False,
    location=['mobile', 'json', 'values']
)
order_details_parser.add_argument(
    'device_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
order_details_parser.add_argument(
    'order_id',
    type=int,
    required=True,
    location=['mobile', 'json', 'values']
)
order_details_parser.add_argument(
    'language',
    type=str,
    required=False,
    default='en',
    location=['mobile', 'json', 'values']
)

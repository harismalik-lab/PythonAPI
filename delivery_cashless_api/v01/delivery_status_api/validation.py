"""
Validation for delivery statuses api
"""
from common.common_helpers import get_request_parser

delivery_statuses_parser = get_request_parser()

delivery_statuses_parser.add_argument(
    'device_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
delivery_statuses_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
delivery_statuses_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)


"""
Validation for menu item status change
"""

from common.common_helpers import get_request_parser

order_refund_parser = get_request_parser()

order_refund_parser.add_argument(
    'order_id',
    type=int,
    required=True,
    location=['mobile', 'json', 'values']
)
order_refund_parser.add_argument(
    'reject_reason',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
order_refund_parser.add_argument(
    'language',
    type=str,
    required=False,
    default='en',
    location=['mobile', 'json', 'values']
)
order_refund_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
order_refund_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
order_refund_parser.add_argument(
    'device_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)

order_refund_parser.add_argument(
    'merchant_pin',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
order_refund_parser.add_argument(
    'refund_amount',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)

"""
Validation for delivery statuses api
"""
from common.common_helpers import get_request_parser
get_orders_history = get_request_parser()

get_orders_history.add_argument(
    'device_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
get_orders_history.add_argument(
    'outlet_sf_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
get_orders_history.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
get_orders_history.add_argument(
    'order_status',
    type=int,
    required=False,
    location=['mobile', 'json', 'values']
)
get_orders_history.add_argument(
    'tracking_number',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
get_orders_history.add_argument(
    'customer_name',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

get_orders_history.add_argument(
    'time_stamp',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

get_orders_history.add_argument(
    'page_num',
    type=int,
    required=False,
    location=['mobile', 'json', 'values']
)

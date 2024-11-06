"""
Validation for Active status management for outlet api
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import boolean

device_online_parser = get_request_parser()

device_online_parser.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values']
)

device_online_parser.add_argument(
    'device_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_online_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_online_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_online_parser.add_argument(
    'device_online_status',
    type=boolean,
    required=True,
    location=['mobile', 'json', 'values'],
)


device_online_check_parser = get_request_parser()

device_online_check_parser.add_argument(
    'language',
    type=str,
    required=False,
    default="en",
    location=['mobile', 'json', 'values']
)

device_online_check_parser.add_argument(
    'device_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'outlet_sf_id',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'merchant_sf_id',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'current_app_version',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'current_battery_status',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'current_free_space',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'is_offline',
    type=boolean,
    required=False,
    default=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'offline_start_time',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'offline_end_time',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'current_network_status',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'current_data_usage',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'monthly_data_usage',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)
device_online_check_parser.add_argument(
    'daily_data_usage',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

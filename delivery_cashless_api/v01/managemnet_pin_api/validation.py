"""
Validation for management api
"""
from common.common_helpers import get_request_parser

management_pin_parser = get_request_parser()

management_pin_parser.add_argument(
    'pin',
    type=str,
    required=True,
    location=['mobile', 'json', 'values']
)

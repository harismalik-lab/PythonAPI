"""
Validation for merchants api
"""
from common.common_helpers import get_request_parser

merchant_parser = get_request_parser()

merchant_parser.add_argument(
    'query',
    type=str,
    required=False,
    location=['mobile', 'json', 'values']
)

merchant_parser.add_argument(
    'language',
    type=str,
    default='en',
    required=False,
    location=['mobile', 'json', 'values']
)

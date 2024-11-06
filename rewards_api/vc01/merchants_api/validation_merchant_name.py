"""
This module contains param validator for /merchantname/<merchant-id> [GET]
"""
from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import language

merchant_name_parser = get_request_parser()

merchant_name_parser.add_argument('offer_id', type=int, required=False,
                                  location=['mobile', 'values', 'json'], default=0)
merchant_name_parser.add_argument('merchant_id', type=int, required=False,
                                  location=['mobile', 'values', 'json'], default=0)
merchant_name_parser.add_argument('language', type=language, default='en',
                                  location=['mobile', 'values', 'json'])
merchant_name_parser.add_argument('session_token', type=str, required=False,
                                  location=['mobile', 'values', 'json'])

from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import boolean, currency

redemption_parser = get_request_parser()
redemption_parser.add_argument(
    'offer_id',
    required=True,
    action='append',
    location=['mobile', 'values', 'json'],
    help='offer_id required (array).'
)
redemption_parser.add_argument(
    'quantity',
    type=str,
    action='append',
    required=True,
    default=[1],
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'isshared',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'outlet_id',
    type=int,
    required=True,
    location=['mobile', 'values', 'json'],
    help='outlet_id required (integer).'
)
redemption_parser.add_argument(
    'merchant_pin',
    type=int,
    required=True,
    location=['mobile', 'values', 'json'],
    help='merchant_pin required (integer).'
)
redemption_parser.add_argument(
    'currency',
    type=currency,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'lng',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'lat',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'is_reattempt',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'transaction_id',
    type=str,
    required=True,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'product_id',
    type=str,
    required=True,
    location=['mobile', 'values', 'json'],
    help='product_id required (integer).'
)
redemption_parser.add_argument(
    'user_id',
    type=int,
    required=True,
    location=['mobile', 'values', 'json'],
    help='user_id required (integer).'
)
redemption_parser.add_argument(
    'location_id',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)
redemption_parser.add_argument(
    'language',
    type=str,
    required=False,
    location=['mobile', 'values', 'json'],
)
redemption_parser.add_argument(
    'session_token',
    type=str,
    required=True,
    location=['mobile', 'values', 'json'],
    help='session_token required (string).'
)

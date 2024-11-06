import re

from flask_restful.inputs import regex

from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import boolean, currency

outlet_parser = get_request_parser()

outlet_parser.add_argument(
    'sort',
    type=regex('^[a-z]+$'),
    required=False,
    default='default',
    help='sort required (alpha only from [a-z]).',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'first_sort_by_redeemability',
    type=boolean,
    default=False,
    required=False,
    help='first_sort_by_redeemability required (true/false) or (1/0)',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'lat',
    type=regex('[0-9\.\-]+'),  # noqa : W605
    required=False,
    help='lng required ([0-9\.\-]+).',  # noqa : W605
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'lng',
    type=regex('[0-9\.\-]+'),  # noqa : W605
    required=False,
    help='lng required ([0-9\.\-]+).',  # noqa : W605
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'radius',
    type=int,
    default=0,
    required=False,
    help='radius required (digits only).',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'query',
    default='',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'query_type',
    type=regex('(name|area|address)', flags=re.IGNORECASE),
    required=False,
    help="'name' of merchant or 'area' or 'address'",
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'category',
    type=str,
    required=False,
    default='All',
    help='Name category to filter outlets by (string only)',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'cuisine',
    type=str,
    required=False,
    default='All',
    help='Cuisine to filter Merchants by (string only)',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'cuisine_filter[]',
    type=str,
    action='append',
    required=False,
    default=[],
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'redeemability',
    type=regex('(all|not_redeemable|redeemed|redeemable|reusable|redeemable_reusable)', flags=re.IGNORECASE),
    default='all',
    required=False,
    help='(all|not_redeemable|redeemed|redeemable|reusable|redeemable_reusable) redeemability is allowed',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'filter_by_type',
    type=regex('(0|1|2|3|4|5|NIL)', flags=re.IGNORECASE),
    default='',
    required=False,
    help='only (0|1|2|3|4|5) filter_by_type is allowed',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'channel',
    type=str,
    required=False,
    default='Mobile',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'neighborhood',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)
outlet_parser.add_argument(
    'location_id',
    type=int,
    default=0,
    required=False,
    help='location_id (integers only)',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'mall',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'hotel',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'offset',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'limit',
    type=int,
    default=60,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'outlet_limit',
    type=int,
    default=60,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'currency',
    type=currency,
    default='USD',
    help='Invalid currency',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'language',
    type=regex('^[a-z]+$'),
    default='en',
    help='Invalid language',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'session_token',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'billing_country',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'outlet_id',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'isshared',
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'product_sku',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'sub_category_filter',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'filters_selected_for_yes[]',
    type=str,
    action='append',
    required=False,
    default=[],
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'filters_selected_for_no[]',
    type=str,
    action='append',
    required=False,
    default=[],
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'is_more_sa',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'include_featured',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'app_version',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'device_key',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'is_cheers',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'is_delivery',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    '__platform',
    type=str,
    default='',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'user_id',
    type=int,
    default=0,
    required=False,
    help='user_id required (integer).',
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'fuzzy',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_parser.add_argument(
    'is_birthday',
    type=boolean,
    default=False,
    required=False,
    location=['mobile', 'values', 'json']
)

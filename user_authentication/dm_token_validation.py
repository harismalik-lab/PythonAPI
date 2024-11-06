from common.common_helpers import get_request_parser

dm_token_parser = get_request_parser()

dm_token_parser.add_argument(
    'merchant_sf_id',
    type=str,
    default='',
    location=['mobile', 'json', 'values'],
    required=False
)
dm_token_parser.add_argument(
    'device_id',
    type=str,
    default='',
    location=['mobile', 'json', 'values'],
    required=False
)
dm_token_parser.add_argument(
    'outlet_sf_id',
    type=str,
    default='',
    location=['mobile', 'json', 'values'],
    required=False
)

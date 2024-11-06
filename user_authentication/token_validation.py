from common.common_helpers import get_request_parser

token_parser = get_request_parser()
token_parser.add_argument(
    '__i',
    type=int,
    default=0,
    location=['mobile', 'json', 'values'],
    required=False
)

token_parser.add_argument(
    '__sid',
    type=int,
    default=0,
    location=['mobile', 'json', 'values'],
    required=False
)

token_parser.add_argument(
    'session_token',
    type=str,
    default='',
    required=False,
    location=['mobile', 'json', 'values'],
    help='request parameter session_token is empty.'
)

token_parser.add_argument(
    'app_version',
    type=str,
    default='',
    location=['mobile', 'json', 'values'],
    required=False
)

token_parser.add_argument(
    'device_key',
    type=str,
    default='',
    location=['mobile', 'json', 'values'],
    required=False
)
token_parser.add_argument(
    'wlcompany',
    type=str,
    default='',
    location=['mobile', 'json', 'values'],
    required=False
)

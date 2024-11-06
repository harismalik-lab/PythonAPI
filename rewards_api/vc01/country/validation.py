"""
Validation for country end point
"""
from flask_restful.inputs import boolean

from common.common_helpers import get_request_parser

country_parser = get_request_parser()
country_parser.add_argument(
    'language',
    type=str,
    default='en',
    required=False,
    location=['mobile', 'values', 'json'],
)
country_parser.add_argument(
    name="istravel",
    default=False,
    type=boolean,
    required=False,
    location=['mobile', 'values', 'json'],
)
country_parser.add_argument(
    name="user_id",
    default=0,
    type=int,
    required=False,
    location=['mobile', 'values', 'json'],
)

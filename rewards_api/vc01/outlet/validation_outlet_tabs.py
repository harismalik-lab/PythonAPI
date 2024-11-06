"""
Validation for outlet tabs action api
"""
from flask_restful.inputs import regex

from common.common_helpers import get_request_parser

outlet_tabs_parser = get_request_parser()
outlet_tabs_parser.add_argument(
    'location_id',
    type=int,
    default=0,
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_tabs_parser.add_argument(
    'language',
    type=regex('[a-z]'),
    default='en',
    required=False,
    location=['mobile', 'values', 'json']
)

outlet_tabs_parser.add_argument(
    'session_token',
    type=str,
    required=False,
    location=['mobile', 'values', 'json']
)

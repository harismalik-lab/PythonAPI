from flask_restful.reqparse import RequestParser

from common.custom_fields_request_parser import boolean

rewards_region_parser = RequestParser(bundle_errors=True)

rewards_region_parser.add_argument(
    'is_travel',
    type=boolean,
    default=False,
    required=False
)
rewards_region_parser.add_argument(
    'language',
    type=str,
    required=False,
    location='args',
    default='en'
)

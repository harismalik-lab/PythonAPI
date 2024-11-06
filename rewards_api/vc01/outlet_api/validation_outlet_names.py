from flask_restful import reqparse
from flask_restful.inputs import regex

outlet_names_parser = reqparse.RequestParser(bundle_errors=True)

outlet_names_parser.add_argument(
    'language',
    type=regex('[a-z]'),
    default='en',
    required=False
)

outlet_names_parser.add_argument(
    'outlet_ids[]',
    type=str,
    action='append',
    default=[],
    required=False
)

outlet_names_parser.add_argument(
    'session_token',
    type=str,
    required=False
)

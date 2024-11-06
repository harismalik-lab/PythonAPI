"""
This module contains param validator for /merchants[GET]
"""
from flask_restful.inputs import regex
from flask_restful.reqparse import RequestParser

from common.custom_fields_request_parser import currency, language

rewards_merchant_parser = RequestParser(bundle_errors=True)

rewards_merchant_parser.add_argument('lat', type=float, default=0, location='args')
rewards_merchant_parser.add_argument('lng', type=float, default=0, location='args')
rewards_merchant_parser.add_argument('redeemability', type=regex('[a-zA-Z]*[_]*'), default='redeemable',
                             location='args')
rewards_merchant_parser.add_argument('currency', type=currency, default='USD', location='args')
rewards_merchant_parser.add_argument('location_id', type=int, default=0, location='args')
rewards_merchant_parser.add_argument('language', type=language, default='en', location='args')

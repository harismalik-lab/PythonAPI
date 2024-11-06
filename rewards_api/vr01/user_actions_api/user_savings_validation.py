from flask_restful.inputs import regex

from common.common_helpers import get_request_parser
from common.custom_fields_request_parser import currency

rewards_user_savings_action_in_parser = get_request_parser()
rewards_user_savings_action_in_parser.add_argument(
    'currency',
    required=False,
    default='USD',
    type=currency,
    location=['mobile', 'values', 'json'],
    help='currency is required'
)
rewards_user_savings_action_in_parser.add_argument(
    'language',
    type=regex('[a-z]'),
    required=False,
    location=['mobile', 'values', 'json'],
    default='en'
)
rewards_user_savings_action_in_parser.add_argument(
    'year',
    type=str,
    required=False,
    location=['mobile', 'values', 'json'],
    default='2016'
)
rewards_user_savings_action_in_parser.add_argument(
    'session_token',
    type=regex('[0-9a-zA-Z]*[-]*'),
    location=['mobile', 'values', 'json'],
    required=False
)
rewards_user_savings_action_in_parser.add_argument(
    '__i',
    type=int,
    location=['mobile', 'values', 'json'],
    required=False
)
rewards_user_savings_action_in_parser.add_argument(
    'magento_customer_id',
    type=int,
    required=False,
    location=['mobile', 'values', 'json'],
    default='0'
)
rewards_user_savings_action_in_parser.add_argument(
    '__platform',
    type=str,
    location=['mobile', 'values', 'json'],
    default="",
    required=False
)

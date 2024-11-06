import datetime

from flask_restful import reqparse

user_login_in_parser = reqparse.RequestParser(bundle_errors=True)
user_login_in_parser.add_argument(
    'username_or_email',
    type=str,
    required=True,
    location=['form', 'json'],
    help='username or email required'
)
user_login_in_parser.add_argument(
    'password',
    type=str,
    required=True,
    location=['form', 'json'],
    help='password required'
)

user_sign_up_parser = reqparse.RequestParser(bundle_errors=True)
user_sign_up_parser.add_argument(
    'password',
    type=str,
    required=True,
    location=['form', 'json'],
    help='password required'
)
user_sign_up_parser.add_argument(
    'username',
    type=str,
    required=True,
    location=['form', 'json'],
    help='username required'
)
user_sign_up_parser.add_argument(
    'first_name',
    type=str,
    required=True,
    location=['form', 'json'],
    help='first_name required'
)
user_sign_up_parser.add_argument('last_name', type=str, required=False, location=['form', 'json'])
user_sign_up_parser.add_argument('gender', type=str, required=False, location=['form', 'json'])
user_sign_up_parser.add_argument('dob', type=datetime, required=False, location=['form', 'json'])
